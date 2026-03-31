import asyncio
from sqlalchemy import select
from app.database import async_session
from app.models.financial import Company, IndustryTemplate, FinancialPeriod, PeriodType, FinancialData

async def seed_supermap_2021():
    async with async_session() as session:
        # Check if SuperMap already exists
        result = await session.execute(select(Company).where(Company.name == "超图软件 (300036)"))
        company = result.scalar_one_or_none()
        if not company:
            print("Company not found. Run the primary seed script first.")
            return

        # Data map for 2021
        data_map = {
            2021: {
                # Income Statement
                "IS_001": 1875094134.37,
                "IS_002": 798745723.82,
                "IS_003": 13386953.73,
                "IS_004": 267696647.83,
                "IS_005": 234823151.00,
                "IS_006": 217296644.74,
                "IS_007": -9888113.75,
                "IS_008": 703810.67,
                "IS_009": 10856702.73,
                "IS_010": 23998860.20,
                "IS_011": 9143009.49,
                "IS_013": -78939275.41,
                "IS_014": -1011808.66,
                "IS_015": 407194.67,
                "IS_101": 10323791.80,
                "IS_102": 117923.53,
                "IS_201": 31470351.55,
                
                # Balance Sheet - Assets
                "BS_A_001": 1387023946.75,
                "BS_A_002": 625011637.15,
                "BS_A_003": 12506171.51,
                "BS_A_004": 747139578.76,
                "BS_A_006": 7339607.95,
                "BS_A_007": 74452520.87,
                "BS_A_008": 487299076.21,
                "BS_A_009": 21879352.67,
                "BS_A_010": 8829945.10,
                "BS_A_201": 1226171.70,
                "BS_A_203": 184333050.75,
                "BS_A_204": 142038845.57,
                "BS_A_205": 112340084.19,
                "BS_A_206": 16801845.53,
                "BS_A_207": 111412831.38,
                "BS_A_208": 707269877.25,
                "BS_A_209": 1155255.04,
                "BS_A_210": 44818803.01,
                
                # Balance Sheet - Liabilities
                "BS_L_001": 5678818.37,
                "BS_L_004": 268136067.84,
                "BS_L_006": 1019465860.93,
                "BS_L_007": 167723635.29,
                "BS_L_008": 54201695.28,
                "BS_L_009": 53206537.27,
                "BS_L_010": 18453093.27,
                "BS_L_011": 33894338.00,
                "BS_L_201": 1218701.92,
                "BS_L_203": 6092766.95,
                "BS_L_206": 21056700.00,
                "BS_L_207": 1745338.06,
                
                # Balance Sheet - Equity
                "BS_E_001": 489550063.00,
                "BS_E_002": 1614003419.21,
                "BS_E_003": -5022538.26,
                "BS_E_004": 85128502.01,
                "BS_E_005": 467880673.61,
            }
        }

        for year, records in data_map.items():
            # Check period
            result = await session.execute(
                select(FinancialPeriod).where(
                    FinancialPeriod.company_id == company.id,
                    FinancialPeriod.year == year,
                    FinancialPeriod.period_type == PeriodType.HISTORICAL
                )
            )
            period = result.scalar_one_or_none()
            if not period:
                period = FinancialPeriod(company_id=company.id, year=year, period_type=PeriodType.HISTORICAL)
                session.add(period)
                await session.commit()
                await session.refresh(period)
            
            # Clear old data
            result = await session.execute(select(FinancialData).where(FinancialData.period_id == period.id))
            old_data = result.scalars().all()
            for d in old_data:
                await session.delete(d)
            
            # Insert new data
            for code, val in records.items():
                item = FinancialData(period_id=period.id, line_item_code=code, value=val)
                session.add(item)
            
            await session.commit()
            print(f"Successfully seeded {year} financial data for {company.name}.")

if __name__ == "__main__":
    asyncio.run(seed_supermap_2021())
