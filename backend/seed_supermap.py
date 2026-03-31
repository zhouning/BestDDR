import asyncio
from sqlalchemy import select
from app.database import async_session
from app.models.financial import Company, IndustryTemplate, FinancialPeriod, PeriodType, FinancialData

async def seed_supermap():
    async with async_session() as session:
        # Get general template
        result = await session.execute(select(IndustryTemplate).where(IndustryTemplate.code == "general"))
        template = result.scalar_one_or_none()
        if not template:
            print("General template not found, please ensure basic seed is run first.")
            return

        # Check if SuperMap already exists
        result = await session.execute(select(Company).where(Company.name == "超图软件 (300036)"))
        company = result.scalar_one_or_none()
        if not company:
            company = Company(name="超图软件 (300036)", industry_template_id=template.id)
            session.add(company)
            await session.commit()
            await session.refresh(company)
            print(f"Created company: {company.name}")
        else:
            print(f"Company already exists: {company.name}")

        # Data map
        data_map = {
            2022: {
                # Income Statement
                "IS_001": 1595688954.43,
                "IS_002": 852979922.83,
                "IS_003": 11159191.98,
                "IS_004": 280178919.76,
                "IS_005": 260555386.47,
                "IS_006": 250997973.09,
                "IS_007": -9370467.11,
                "IS_008": 1572597.37,
                "IS_009": 11133808.52,
                "IS_010": 46299683.26,
                "IS_011": 22665948.68,
                "IS_013": -116027646.71,
                "IS_014": -274970971.30,
                "IS_015": -2916403.22,
                "IS_101": 10267387.99,
                "IS_102": 1388448.06,
                "IS_201": -23065031.99,
                
                # Balance Sheet - Assets
                "BS_A_001": 930060674.73,
                "BS_A_002": 798010995.18,
                "BS_A_003": 7011537.02,
                "BS_A_004": 673678613.65,
                "BS_A_006": 2797935.64,
                "BS_A_007": 70100032.41,
                "BS_A_008": 496282644.00,
                "BS_A_009": 36518122.71,
                "BS_A_010": 2120615.10,
                "BS_A_201": 82705679.72,
                "BS_A_202": 14000000.00, # mapped to other non-current
                "BS_A_203": 177428468.19,
                "BS_A_204": 269218535.02,
                "BS_A_206": 17130899.11,
                "BS_A_207": 178246600.37,
                "BS_A_208": 445407170.79,
                "BS_A_209": 5460819.12,
                "BS_A_210": 70599259.64,
                
                # Balance Sheet - Liabilities
                "BS_L_001": 11841832.94,
                "BS_L_004": 336817442.70,
                "BS_L_006": 976706254.37,
                "BS_L_007": 129158222.32,
                "BS_L_008": 26425368.76,
                "BS_L_009": 38856968.87,
                "BS_L_010": 14781249.73,
                "BS_L_011": 38563242.88,
                "BS_L_201": 1933383.45,
                "BS_L_203": 2760302.66,
                "BS_L_206": 2816700.00,
                
                # Balance Sheet - Equity
                "BS_E_001": 489550063.00,
                "BS_E_002": 1615474930.38,
                "BS_E_003": -2197568.08,
                "BS_E_004": 91463799.56,
                "BS_E_005": 618456806.35,
            },
            2023: {
                # Income Statement
                "IS_001": 1978685866.97,
                "IS_002": 833390081.68,
                "IS_003": 12140997.83,
                "IS_004": 376648808.88,
                "IS_005": 280729048.31,
                "IS_006": 262454614.35,
                "IS_007": -6276293.70,
                "IS_008": 1600468.61,
                "IS_009": 8332881.36,
                "IS_010": 28836329.21,
                "IS_011": 24862801.56,
                "IS_013": -111708072.58,
                "IS_014": -20715267.91,
                "IS_015": -28092.50,
                "IS_101": 16294070.66,
                "IS_102": 2759759.01,
                "IS_201": 9010042.37,

                # Balance Sheet - Assets
                "BS_A_001": 1063632894.19,
                "BS_A_002": 757009473.73,
                "BS_A_003": 9370494.63,
                "BS_A_004": 715630040.15,
                "BS_A_006": 1274715.94,
                "BS_A_007": 44105450.10,
                "BS_A_008": 446475355.50,
                "BS_A_009": 49588472.05,
                "BS_A_010": 1249359.10,
                "BS_A_201": 85891976.24,
                "BS_A_202": 14000000.00,
                "BS_A_203": 170634582.98,
                "BS_A_204": 263215587.32,
                "BS_A_206": 19363492.29,
                "BS_A_207": 197963090.30,
                "BS_A_208": 430316222.02,
                "BS_A_209": 5360810.95,
                "BS_A_210": 82031300.45,
                
                # Balance Sheet - Liabilities
                "BS_L_001": 10392476.32,
                "BS_L_004": 395662811.34,
                "BS_L_006": 812746737.08,
                "BS_L_007": 147140600.91,
                "BS_L_008": 44991529.69,
                "BS_L_009": 38768753.38,
                "BS_L_010": 12412507.28,
                "BS_L_011": 30936401.81,
                "BS_L_201": 1983792.22,
                "BS_L_203": 7655948.52,
                "BS_L_206": 2816700.00,
                
                # Balance Sheet - Equity
                "BS_E_001": 492766617.00,
                "BS_E_002": 1649442795.67,
                "BS_E_003": -716253.16,
                "BS_E_004": 101638415.30,
                "BS_E_005": 760392679.59,
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
    asyncio.run(seed_supermap())