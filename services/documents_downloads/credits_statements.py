from fastapi import HTTPException,status
from fastapi.responses import StreamingResponse
from io import BytesIO
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select
from decimal import Decimal
from datetime import datetime,date,time,timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_RIGHT,TA_CENTER
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle)
from reportlab.pdfgen import canvas
from crud.clients import ClientsCrudClass
from utils.logging.logger import define_logger
from models.credits import Credits_History_Table

statements_logger=define_logger("statements_logger","logs/statements_route.log")

# This is tight coupling breaking SOLID principles

clients_object=ClientsCrudClass()


def money(value: Decimal | int | float) -> str:
    return f"{Decimal(value):,.2f}"


def normalize_signed_amount(tx_type, amount) -> Decimal:
    
    """
    Convert your transaction into a signed amount.
    Assumption:
    - Deposit adds credits
    - Withdrawal removes credits
    - Unknown treated as positive unless you change it

    Adjust this mapping to match your enum values exactly.
    """
    amount = Decimal(amount or 0)
    tx_value = getattr(tx_type, "value", str(tx_type)).lower()

    if tx_value == "withdrawal":
        return -amount
    return amount


def pdf_header_footer(canvas, doc):
    canvas.saveState()
    page_width, page_height = A4
    # Header line
    canvas.setStrokeColor(colors.HexColor("#d1d5db"))
    canvas.setLineWidth(0.5)
    canvas.line(15 * mm, page_height - 18 * mm, page_width - 15 * mm, page_height - 18 * mm)
    # Footer line
    canvas.line(15 * mm, 15 * mm, page_width - 15 * mm, 15 * mm)
    # Footer text
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#6b7280"))
    canvas.drawString(15 * mm, 10 * mm, "Credits Statement")
    canvas.drawRightString(page_width - 15 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()



class CreditsDocuments:

    def __init__(self,clients:ClientsCrudClass):
        self.clients=clients
    async def get_current_client(self,client_id:int,session:AsyncSession):
        return await self.clients.get_single_client_crud(client_id=client_id,session=session)
        
    async def download_credits_pdf_statements(self,user_id:int,start_date:date,end_date:date,session:AsyncSession):
        
        try:
            current_client=await self.get_current_client(client_id=user_id,session=session)
            #build date boundaries
            start_dt=None
            end_dt=None
            if start_date:
                start_dt=datetime.combine(start_date,time.min).replace(tzinfo=timezone.utc)
            
            if end_date:
                end_dt=datetime.combine(end_date,time.max).replace(tzinfo=timezone.utc)
            #Opening balance = all signed transactions before start_date
            opening_balance=Decimal("0.00")
            opening_stmt=select(Credits_History_Table.credits_amount,Credits_History_Table.transaction_type).where(Credits_History_Table.created_by==user_id)
            if start_dt:
                opening_stmt=opening_stmt.where(Credits_History_Table.created_at< start_dt)
            
            opening_result=await session.execute(opening_stmt)
            opening_rows=opening_result.all()

            for row in opening_rows:
                opening_balance+=normalize_signed_amount(row.transaction_type,row.credits_amount)
            #statement-period transactions
            tx_stmt=(select(Credits_History_Table.history_id,Credits_History_Table.credits_amount,Credits_History_Table.transaction_type,Credits_History_Table.is_active,Credits_History_Table.created_at).where(Credits_History_Table.created_by==user_id).order_by(Credits_History_Table.created_at.asc()))

            if start_dt:
                tx_stmt=tx_stmt.where(Credits_History_Table.created_at >=start_dt)
            
            if end_dt:
                tx_stmt=tx_stmt.where(Credits_History_Table.created_at <= end_dt)

            tx_result=await session.execute(tx_stmt)
            tx_rows=tx_result.all()
            # 3) Totals inside statement period
            total_deposits = Decimal("0.00")
            total_withdrawals = Decimal("0.00")
            running_balance = opening_balance

            table_rows = [[
                "Date",
                "Reference",
                "Type",
                "Deposit",
                "Withdrawal",
                "Running Balance",
            ]]

            for row in tx_rows:
                tx_type_raw = getattr(row.transaction_type, "value", str(row.transaction_type))
                tx_type = tx_type_raw.lower()
                amount = Decimal(row.credits_amount or 0)
                deposit_value = Decimal("0.00")
                withdrawal_value = Decimal("0.00")

                if tx_type == 'Deposit':
                    deposit_value=amount
                    total_deposits+=amount
                    running_balance+=amount
                
                elif tx_type=="Withdrawal":
                    withdrawal_value=amount
                    total_withdrawals+=amount
                    running_balance-=amount
                
                else:
                    #fallback rule
                    deposit_value=amount
                    total_deposits+=amount
                    running_balance+=amount

                table_rows.append([
                row.created_at.strftime("%Y-%m-%d %H:%M") if row.created_at else "",
                str(row.history_id),
                tx_type_raw,
                money(deposit_value) if deposit_value else "-",
                money(withdrawal_value) if withdrawal_value else "-",
                money(running_balance),
                    ])

            closing_balance = opening_balance + total_deposits - total_withdrawals

            if len(table_rows) == 1:
                    table_rows.append(["-", "-", "No transactions", "-", "-", money(opening_balance)])

            #Build PDF
            pdf_buffer=BytesIO()

            document=SimpleDocTemplate(
                    pdf_buffer,
                    pagesize=A4,
                    leftMargin=15*mm,
                    rightMargin=15*mm,
                    topMargin=22*mm,
                    bottomMargin=20*mm,
                    title="Credits Statements",
                    author="Ping API Service"
                )

            styles=getSampleStyleSheet()
            styles.add(ParagraphStyle(name="SmallMuted",parent=styles["Normal"],fontSize=9,textColor=colors.HexColor("#6b7280")))
            styles.add(ParagraphStyle(name="RightHeading",parent=styles["Heading2"],alignment=TA_RIGHT))
            styles.add(ParagraphStyle(name="CenterSmall",parent=styles["Normal"],alignment=TA_CENTER,fontSize=8,textColor=colors.HexColor("#6b7280")))
            elements = []

             # Title block
            elements.append(Paragraph("Credits Statement", styles["Title"]))
            elements.append(Spacer(1, 3))

            period_label = "Full history"

            if start_date or end_date:
                    period_label = f"Period: {start_date or 'Beginning'} to {end_date or 'Today'}"

            generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

            elements.append(Paragraph(f"Client Name: {current_client.client_name}", styles["Normal"]))
            elements.append(Paragraph(period_label, styles["Normal"]))
            elements.append(Paragraph(f"Generated at: {generated_at}", styles["SmallMuted"]))
            elements.append(Spacer(1, 10))

                 # Summary section
            summary_data = [
                    ["Opening Balance", money(opening_balance), "Total Deposits", money(total_deposits)],
                    ["Total Withdrawals", money(total_withdrawals), "Closing Balance", money(closing_balance)],
                ]

            summary_table = Table(summary_data, colWidths=[40 * mm, 35 * mm, 40 * mm, 35 * mm])

            summary_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f9fafb")),
                    ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#d1d5db")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("ALIGN", (3, 0), (3, -1), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ]))

            elements.append(summary_table)
            elements.append(Spacer(1, 14))

            # Transactions heading
            elements.append(Paragraph("Transaction History", styles["Heading2"]))
            elements.append(Spacer(1, 6))

            transactions_table = Table(table_rows,colWidths=[32 * mm, 22 * mm, 28 * mm, 28 * mm, 30 * mm, 35 * mm],repeatRows=1)

            transactions_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d1d5db")),
                    ("ALIGN", (1, 1), (1, -1), "CENTER"),
                    ("ALIGN", (3, 1), (5, -1), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ]))

            elements.append(transactions_table)
            elements.append(Spacer(1, 12))
            elements.append(Paragraph("This document was generated electronically from the credits service.",styles["CenterSmall"]))
            document.build(elements,onFirstPage=pdf_header_footer,onLaterPages=pdf_header_footer)
            pdf_buffer.seek(0)
            filename = f"credits_statement_{user_id}_{datetime.now(timezone.utc):%Y%m%d_%H%M%S}.pdf"
            statements_logger.info(f"client:{current_client.client_name} with email:{current_client.client_email} downloaded transaction history document")

            return StreamingResponse(pdf_buffer,media_type="application/pdf",headers={"Content-Disposition": f'attachment; filename="{filename}"'})
        
        except Exception as e:

            statements_logger.exception(f"an internal server error occurred while downloading credits statements for user:{user_id},expception:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an internal server error occurred while downloading credits pdf statements")

