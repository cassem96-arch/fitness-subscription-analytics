# Power BI build guide: report.pbix

Follow these steps in Power BI Desktop on Windows to build `report.pbix`. When you finish, every visual should match the numbers in `README.md`. (A .pbix file can only be created in Power BI Desktop.)

## Task 1: Load the data and build the model

1. **Home > Get data > Excel workbook** and pick `data/Fitness_Subscriptions_Dataset.xlsx`. Tick **customers** and **transactions**, then click **Transform Data**.
2. In Power Query, select `transactions` and check the icon on the `Transaction_Date` column header. It must be the calendar icon (**Date**). If it shows ABC/123 or Date/Time, right-click the column and choose **Change Type > Date**. Also check that `Revenue` is Whole Number and `CAC` (in customers) is Decimal Number. Click **Close & Apply**.
3. **Modeling > New table** and paste:
```DAX
dim_date =
ADDCOLUMNS (
    CALENDAR ( MIN ( transactions[Transaction_Date] ), MAX ( transactions[Transaction_Date] ) ),
    "Year", YEAR ( [Date] ),
    "Month Number", MONTH ( [Date] ),
    "Month", FORMAT ( [Date], "MMM yyyy" ),
    "StartOfMonth", DATE ( YEAR ( [Date] ), MONTH ( [Date] ), 1 )
)
```
   Select `dim_date` in the Data pane, then choose **Table tools > Mark as date table** and pick column `Date`. Select the `StartOfMonth` column and set **Column tools > Data type = Date**, **Format = mmm yyyy**.
4. **Model view**: drag `customers[Customer_ID]` onto `transactions[Customer_ID]` (One-to-many, Single direction). Then drag `dim_date[Date]` onto `transactions[Transaction_Date]` (One-to-many, Single direction). Delete any other relationship Power BI auto-created.
5. Take a screenshot of the Model view and save it as `screenshots/data_model.png`.

## Calculated columns

In the Data pane, select the table, choose **Table tools > New column**, and paste each formula.

**customers** table:
```DAX
Cohort Month =
VAR FirstDate = CALCULATE ( MIN ( transactions[Transaction_Date] ) )
RETURN DATE ( YEAR ( FirstDate ), MONTH ( FirstDate ), 1 )
```
Set the data type to Date and the format to `mmm yyyy`.
```DAX
Cohort Year = YEAR ( customers[Cohort Month] )
```
**transactions** table:
```DAX
Months Since Cohort =
DATEDIFF ( RELATED ( customers[Cohort Month] ), transactions[Transaction_Date], MONTH )
```
(Set the data type to Whole Number. Its values should run from 0 to 24.)

## Measures

Select the **transactions** table and choose **Home > New measure** for each:
```DAX
Total Revenue = SUM ( transactions[Revenue] )

Subscription Revenue =
CALCULATE ( SUM ( transactions[Revenue] ), transactions[Transaction_Type] = "Subscription" )

Active Customers =
CALCULATE ( DISTINCTCOUNT ( transactions[Customer_ID] ), transactions[Transaction_Type] = "Subscription" )

Cohort Size =
CALCULATE (
    DISTINCTCOUNT ( transactions[Customer_ID] ),
    REMOVEFILTERS ( transactions[Months Since Cohort] ),
    transactions[Months Since Cohort] = 0,
    transactions[Transaction_Type] = "Subscription"
)

Retention % = DIVIDE ( [Active Customers], [Cohort Size] )

Cumulative LTV =
VAR CurrentDate = MAX ( dim_date[Date] )
RETURN
    CALCULATE ( [Total Revenue], FILTER ( ALL ( dim_date ), dim_date[Date] <= CurrentDate ) )

Total CAC = SUM ( customers[CAC] )

Break-even Month =
MINX (
    FILTER ( VALUES ( dim_date[StartOfMonth] ), [Cumulative LTV] >= [Total CAC] ),
    dim_date[StartOfMonth]
)
```
Format `Retention %` as Percentage with 1 decimal place. Format `Total Revenue`, `Subscription Revenue`, `Cumulative LTV` and `Total CAC` as Currency. Format `Break-even Month` as `mmm yyyy`.

## Task 2: Customer Cohort page

1. Rename the page (double-click the tab) to **Customer Cohort**.
2. Add a **Matrix** visual with:
   - **Rows:** `customers[Cohort Month]`. In the field well, click the arrow and choose **Cohort Month** instead of Date Hierarchy.
   - **Columns:** `transactions[Months Since Cohort]`.
   - **Values:** `Retention %`.
3. Under **Format visual > Cell elements**, turn on **Background color** and pick a gradient: lowest value red, highest value green. That is the color scale.
4. Turn off row and column subtotals (**Format > Row subtotals / Column subtotals = Off**).
5. Check: the Months Since Cohort = 0 column shows 100% in every row. The Jan 2024 row should read 100%, 85%, 78%, 50%, ... and month 3 should be about 50% for every cohort.
6. Take a screenshot and save it as `screenshots/cohort_analysis.png`.

## Task 3: Revenue Forecast page

1. Add a new page and name it **Revenue Forecast**.
2. Add a **Line chart** with **X-axis** `dim_date[StartOfMonth]` (choose **StartOfMonth**, not the Date Hierarchy) and **Y-axis** `Subscription Revenue`.
3. **Format visual > X-axis > Type = Continuous**. The forecast only works on a continuous date axis.
4. Open the **Analytics** pane (the magnifying-glass icon), choose **Forecast > Add**, and set:
   - **Units:** Months, **Forecast length:** 12
   - **Ignore the last:** 0
   - **Seasonality:** 12 (points)
   - **Confidence interval:** 95%
   
   Click **Apply**.
5. Check: actual values run from $6,034 (Jan 2024) to $165,465 (Jan 2026), and the forecast extends to Jan 2027. Power BI's forecast values may differ slightly from the Python approximation in the README. Hover over Feb 2026 and Jan 2027 and compare them. If they differ, put the Power BI tooltip values into the README forecast table.
6. Take a screenshot and save it as `screenshots/revenue_forecast.png`.

## Task 4: CAC vs. LTV page

1. Add a new page and name it **CAC vs. LTV**.
2. Add a **Line chart** with **X-axis** `dim_date[StartOfMonth]` (Continuous) and **Y-axis** `Cumulative LTV`.
3. In the **Analytics** pane, add a **Constant line**. Next to **Value**, click the **fx** button, choose **Field value**, and pick the `Total CAC` measure. Label it "Total CAC" and turn on **Data label**.
4. Add a **Slicer** with `customers[Cohort Year]`. Set **Format > Slicer settings > Style = Tile** (or Dropdown) and turn on **Single select**.
5. Add a **Card** visual with `Break-even Month`, and optionally a card with `Total CAC`.
6. Check:
   - With **2024** selected: Total CAC = **$501,536.80**, and the line crosses the CAC line in **Dec 2024** (Cumulative LTV $528,892). Break-even Month card = Dec 2024.
   - With **2025** selected: Total CAC = **$1,162,459.11**, crossing in **Dec 2025** (Cumulative LTV $1,231,980). Break-even Month card = Dec 2025.
7. Take a screenshot (2024 selected is fine; one with each year is better) and save it as `screenshots/cac_vs_ltv.png`.

## Save and upload

1. **File > Save as** `report.pbix` in the repo folder (next to README.md).
2. Replace the four PNGs in `screenshots/` with your real Power BI screenshots, using the same file names.
3. Upload `report.pbix` and the new screenshots to the GitHub repo `fitness-subscription-analytics`, then submit the repo URL.
