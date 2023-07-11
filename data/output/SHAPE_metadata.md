# Variables description for the Synthetic Household/Accommodation Population for Energy (SHAPE)

```
HID: {Household ID}
```

## Geographic Identifiers

* Related Source: Postcode to Output Area to Lower Layer Super Output Area to
  Middle Layer Super Output Area to Local Authority District (February 2022)
  Lookup in the UK - Office for National Statistics (ONS).

```
LADNM : {Local Authority District Name}
LADCD : {Local Authority District Code}
OA: {Output Area}
```

## Accommodation type

* Related Census Table: LC4402

```
"LC4402_C_TYPACCOM": {
  "0": "All categories: Accommodation type",
  "1": "Whole house or bungalow: Total",
  "2": "Whole house or bungalow: Detached",
  "3": "Whole house or bungalow: Semi-detached",
  "4": "Whole house or bungalow: Terraced (including end-terrace)",
  "5": "Flat, maisonette or apartment, or mobile/temporary accommodation"
}
```

## Tenure

* Related Census Table: LC4402

```
"C_TENHUK11": {
  "0": "All categories: Tenure",
  "1": "Owned or shared ownership: Total",
  "2": "Owned: Owned outright",
  "3": "Owned: Owned with a mortgage or loan or shared ownership",
  "4": "Rented or living rent free: Total",
  "5": "Rented: Social rented",
  "6": "Rented: Private rented or living rent free"
}
```

## Household type (alternative)

Related Census Table: LC4408

```
"C_AHTHUK11": {
  "0": "All categories: Household type",
  "1": "married couple family",
  "2": "same-sex civil partnership couple family",
  "3": "cohabiting couple family",
  "4": "lone parent family"
}
```

## Household size

* Related Census Table: LC4404

```
"C_SIZHUK11": {
  "0": "All categories: Household size",
  "1": "1 person in household",
  "2": "2 people in household",
  "3": "3 people in household",
  "4": "4 or more people in household"
  }
```

## Number of rooms

* Related Census Table: LC4404

```
"C_ROOMS": {
  "0": "All categories: Number of rooms",
  "1": "1 room",
  "2": "2 rooms",
  "3": "3 rooms",
  "4": "4 rooms",
  "5": "5 rooms",
  "6": "6 or more rooms"
}
```

## Number of bedrooms

* Related Census Table: LC4405EW

```
"C_BEDROOMS": {
  "0": "All categories: Number of bedrooms",
  "1": "1 bedroom",
  "2": "2 bedrooms",
  "3": "3 bedrooms",
  "4": "4 or more bedrooms"
}
```


## Type of central heating in household

* Related Census Table: LC4402

```
"C_CENHEATHUK11": {
  "0": "All categories: Type of central heating in household",
  "1": "Does not have central heating",
  "2": "Does have central heating"
}
```

## NS-SeC - Household Reference Person

* Related Census Table: LC4605

```
"C_NSSEC": {
  "0": "All categories: NS-SeC",
  "1": "1. Higher managerial, administrative and professional occupations",
  "2": "2. Lower managerial, administrative and professional occupations",
  "3": "3. Intermediate occupations",
  "4": "4. Small employers and own account workers",
  "5": "5. Lower supervisory and technical occupations",
  "6": "6. Semi-routine occupations",
  "7": "7. Routine occupations",
  "8": "8. Never worked and long-term unemployed",
  "9": "L15 Full-time students",
  "10": "L17 Not classifiable for other reasons"
}
```


## Ethnic group of Household Reference Person (HRP)

* Related Census Table: LC4202

```
"C_ETHHUK11": {
  "0": "All categories: Ethnic group of HRP",
  "1": "White: Total",
  "2": "White: English/Welsh/Scottish/Northern Irish/British",
  "3": "White: Irish",
  "4": "White: Other White",
  "5": "Mixed/multiple ethnic group",
  "6": "Asian/Asian British",
  "7": "Black/African/Caribbean/Black British",
  "8": "Other ethnic group"
}
```

## Car or van availability

* Related Census Table: LC4202

```
"C_CARSNO": {
  "0": "All categories: Car or van availability",
  "1": "No cars or vans in household",
  "2": "1 car or van in household",
  "3": "2 or more cars or vans in household"
}
```

## Floor Area

* Related Source: EPC

```
"FLOOR_AREA": {
  "0": "All categories: Total floor area",
  "1": "0 < A <= 25 m²",
  "2": "25 < A <= 50",
  "3": "50 < A <= 75",
  "4": "75 < A <= 100",
  "5": "100 < A <= 125",
  "6": "125 < A <= 150",
  "7": "150 < A <= 175",
  "8": "175 < A <= 200",
  "9": "200 < A <= 225",
  "10": "225 < A <= 250",
  "11": "250 < A <= 275",
  "12": "275 < A <= 300",
  "13": "300 < A <= 325",
  "14": "325 < A <= 350",
  "15": "350< A <= 375",
  "16": "375< A <= 400",
  "17": "400< A <= 425",
  "18": "425< A <= 450",
  "19": "450< A <= 475",
  "20": "475< A <= 500"
}
```

## Accommodation age

* Related Source: EPC

```
"ACCOM_AGE": {
  "0": "All categories: Construction age band",
  "1": "Pre 1930",
  "2": "1930-1949",
  "3": "1950-1966",
  "4": "1967-1975",
  "5": "1976-1982",
  "6": "1983-1990",
  "7": "1991-1995",
  "8": "1996-2002",
  "9": "2003-2006",
  "10": "Post-2006"
}
```

## Glas Flag

* Related Source: EPC

```
"GAS": {
  "0": "All categories: Gas presence flag",
  "1": "No",
  "2": "Yes"
}
```