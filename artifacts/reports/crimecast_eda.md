# SITAKA EDA Report

- Rows: `20000`
- Columns: `17`
- Task: `tabular_classification`
- Target: `Crime_Category`

## Column Summary

| Column | Type | Missing | Unique |
| --- | --- | ---: | ---: |
| `Latitude` | `float64` | 0 | 64 |
| `Longitude` | `float64` | 0 | 52 |
| `Area_ID` | `float64` | 0 | 21 |
| `Area_Name` | `object` | 0 | 21 |
| `Part 1-2` | `float64` | 0 | 2 |
| `Victim_Age` | `float64` | 0 | 98 |
| `Victim_Sex` | `object` | 0 | 5 |
| `Victim_Descent` | `object` | 0 | 18 |
| `Crime_Category` | `object` | 0 | 6 |
| `occurred_year` | `int64` | 0 | 1 |
| `occurred_month` | `int64` | 0 | 12 |
| `occurred_day_of_week` | `int64` | 0 | 7 |
| `occurred_hour` | `float64` | 0 | 24 |
| `report_lag_bucket` | `object` | 0 | 5 |
| `has_weapon` | `int64` | 0 | 2 |
| `victim_age_missing` | `int64` | 0 | 1 |
| `premise_group` | `object` | 0 | 21 |

## Numeric Summary

| Index | Latitude | Longitude | Area_ID | Part 1-2 | Victim_Age | occurred_year | occurred_month | occurred_day_of_week | occurred_hour | has_weapon | victim_age_missing |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| count | 20000.0 | 20000.0 | 20000.0 | 20000.0 | 20000.0 | 20000.0 | 20000.0 | 20000.0 | 20000.0 | 20000.0 | 20000.0 |
| mean | 33.9405 | -117.8931 | 10.8343 | 1.4182 | 30.1354 | 2020.0 | 6.4323 | 3.0224 | 13.3528 | 0.3668 | 0.0 |
| std | 2.1268 | 7.3777 | 6.0332 | 0.4933 | 21.8631 | 0.0 | 3.4592 | 1.9766 | 6.463 | 0.4819 | 0.0 |
| min | 0.0 | -118.66 | 1.0 | 1.0 | 0.0 | 2020.0 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| 25% | 34.01 | -118.43 | 6.0 | 1.0 | 12.0 | 2020.0 | 3.0 | 1.0 | 9.0 | 0.0 | 0.0 |
| 50% | 34.06 | -118.32 | 11.0 | 1.0 | 31.0 | 2020.0 | 6.0 | 3.0 | 14.0 | 0.0 | 0.0 |
| 75% | 34.1625 | -118.27 | 16.0 | 2.0 | 46.0 | 2020.0 | 9.0 | 5.0 | 19.0 | 1.0 | 0.0 |
| max | 34.33 | 0.0 | 21.0 | 2.0 | 99.0 | 2020.0 | 12.0 | 6.0 | 23.0 | 1.0 | 0.0 |

## Target Summary

| Value | Count |
| --- | ---: |
| `Property Crimes` | 11666 |
| `Violent Crimes` | 4767 |
| `Crimes against Public Order` | 1808 |
| `Fraud and White-Collar Crimes` | 1355 |
| `Crimes against Persons` | 225 |
| `Other Crimes` | 179 |

## Correlation Warnings

- `Latitude` and `Longitude` are highly correlated: `0.999`

## Leakage Hints

No obvious column-name leakage hints detected.
