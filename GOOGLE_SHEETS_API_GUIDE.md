# Google Sheets API Guide (with gspread)

This guide explains how to interact with Google Sheets programmatically using the `gspread` library, which wraps the official Google Sheets API v4.

## 1. Core Concepts

*   **Spreadsheet**: The entire file (like an Excel workbook). Identified by a long ID string in the URL.
*   **Worksheet**: A single tab within the spreadsheet (e.g., "Sheet1", "Data"). Identified by a name (string) or an ID (integer).
*   **Range**: A selection of cells, usually described in **A1 Notation** (e.g., `A1:B10`).
*   **A1 Notation**:
    *   `A1`: Column A, Row 1.
    *   `A1:B5`: A rectangle from A1 to B5.
    *   `A:A`: The entire column A.
    *   `1:1`: The entire row 1.
    *   `Sheet1!A1:B5`: Specific range in a specific sheet.

## 2. Reading Data

There are several ways to read data depending on how you want the output structured.

### A. List of Dictionaries (`get_all_records`)
Best for structured data with headers in the first row.
```python
# Sheet:
# | Name  | Age |
# | Alice | 30  |
# | Bob   | 25  |

data = worksheet.get_all_records()
# Result: [{'Name': 'Alice', 'Age': 30}, {'Name': 'Bob', 'Age': 25}]
```

### B. List of Lists (`get_all_values`)
Returns the raw matrix of values. Useful if you don't have headers or want everything as strings.
```python
data = worksheet.get_all_values()
# Result: [['Name', 'Age'], ['Alice', '30'], ['Bob', '25']]
```

### C. Specific Range (`get`)
Read only a specific subset of data.
```python
# Read only column A
names = worksheet.get('A2:A10')
# Result: [['Alice'], ['Bob'], ...]
```

### D. Single Cell (`acell` or `cell`)
```python
val = worksheet.acell('B2').value  # Using A1 notation -> '30'
val = worksheet.cell(2, 2).value   # Using Row, Col coordinates -> '30'
```

## 3. Writing Data

### A. Update Range (`update`)
The most common way to write a block of data.
```python
# Write to A1:B2
worksheet.update('A1:B2', [['Name', 'Age'], ['Alice', 30]])
```
*Note: In newer gspread versions, `update` handles lists of lists automatically.*

### B. Append Row (`append_row`)
Adds a new row to the first empty line at the bottom.
```python
worksheet.append_row(['Charlie', 35])
```

### C. Single Cell Update (`update_acell` or `update_cell`)
```python
worksheet.update_acell('B2', 31)
worksheet.update_cell(2, 2, 31)
```

### D. Writing Dictionaries
Since Sheets are 2D grids, you can't "write a dictionary" directly. You must map it to rows/columns.

**Scenario 1: List of Dictionaries (Rows)**
If you have `[{'Name': 'Alice', 'Age': 30}, {'Name': 'Bob', 'Age': 25}]`:
1.  **Get Headers**: Read the first row to know the column order.
2.  **Map Values**: Convert each dict to a list based on those headers.

```python
# 1. Define your data
new_records = [
    {'Name': 'Alice', 'Age': 30},
    {'Name': 'Bob', 'Age': 25}
]

# 2. Get current headers (assuming they are in row 1)
headers = worksheet.row_values(1) # e.g., ['Name', 'Age', 'City']

# 3. Prepare rows
rows_to_write = []
for record in new_records:
    # Create a row list, using None or "" for missing keys
    row = [record.get(header, "") for header in headers]
    rows_to_write.append(row)

# 4. Append them
worksheet.append_rows(rows_to_write)
```

**Scenario 2: Key-Value Pairs (Vertical)**
If you want to write `{'Config': 'A', 'Value': 100}` as two columns:
```python
data_dict = {'Config': 'A', 'Value': 100}
# Convert to list of lists: [['Config', 'A'], ['Value', 100]]
matrix = [[k, v] for k, v in data_dict.items()]

worksheet.update('A1', matrix)
```

## 4. Advanced & Efficient Operations

### Batch Updates (`batch_update`)
**Crucial for performance.** Every call to `update` or `append_row` is an HTTP request. The API has limits (quotas). If you need to update 100 disconnected cells, doing it one by one will be slow and might hit rate limits.

`batch_update` allows you to send multiple changes in a single API call.

```python
# Example: Update A1 and C5 in one go
worksheet.batch_update([
    {'range': 'A1', 'values': [['New Header']]},
    {'range': 'C5', 'values': [['New Data']]}
])
```

### Clearing Data
```python
worksheet.clear()       # Clears everything
worksheet.resize(rows=1) # Clears and deletes extra rows (useful for full overwrites)
```

## 5. Formatting (Visuals)

You can change cell colors, fonts, and borders.
```python
# Make header row bold
worksheet.format('A1:B1', {'textFormat': {'bold': True}})

# Change background color
worksheet.format('A2:B2', {
    'backgroundColor': {
        'red': 1.0, 'green': 0.0, 'blue': 0.0 # Red
    }
})
```

## 6. API Quotas & Limits

*   **Read Requests**: Unlimited for most practical purposes, but rate-limited (e.g., 60 requests per minute per user).
*   **Write Requests**: Also rate-limited (e.g., 60 requests per minute per user).
*   **Cell Limit**: A single spreadsheet can have up to 10 million cells.

**Best Practice**: Always try to read or write in **chunks** (bulk) rather than cell-by-cell loops to stay within limits and improve speed.
