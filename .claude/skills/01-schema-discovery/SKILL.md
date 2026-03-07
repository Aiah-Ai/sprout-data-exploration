# Skill 01: Schema Discovery
### Session 1 — Map the complete Databricks schema from scratch

---

## Objective
Build a comprehensive data dictionary of the entire Databricks warehouse so that
all subsequent sessions know exactly what data is available, where it lives, and
what it looks like. No analysis happens here — only discovery and documentation.

---

## How to Execute SQL

All SQL queries should be executed via the Databricks CLI:

```bash
databricks sql --query "YOUR SQL HERE"
```

For multi-line queries, use a heredoc:

```bash
databricks sql --query "$(cat <<'SQL'
SELECT
  company_id,
  COUNT(*) AS total
FROM some_table
GROUP BY company_id
SQL
)"
```

---

## Step 1: Catalog → Schema → Table Inventory

Enumerate every object in the warehouse:

```sql
-- List all catalogs
SHOW CATALOGS;

-- For each catalog, list schemas
SHOW SCHEMAS IN <catalog>;

-- For each schema, list tables
SHOW TABLES IN <catalog>.<schema>;
```

Record every `catalog.schema.table` path in `output/schema_map.md`.

---

## Step 2: HR Relevance Scoring

Score every table by HR relevance using keyword tiers.

### Keyword Tiers

**Tier 1 — Core HR** (score 5): Tables whose names or column names contain:
`employee`, `headcount`, `termination`, `attrition`, `turnover`, `hire`,
`compensation`, `salary`, `pay`, `performance`, `review`, `rating`,
`engagement`, `absence`, `leave`, `tenure`, `promotion`

**Tier 2 — HR-Adjacent** (score 3): Tables containing:
`department`, `org`, `position`, `job`, `role`, `team`, `manager`,
`benefit`, `training`, `learning`, `succession`, `workforce`, `staff`,
`recruit`, `candidate`, `onboard`, `offboard`, `diversity`, `equity`

**Tier 3 — Contextual** (score 1): Tables containing:
`company`, `client`, `organization`, `location`, `office`, `cost_center`,
`budget`, `headcount_plan`, `forecast`

**Tier 0 — Not relevant** (score 0): System tables, audit logs, metadata tables
with no HR content.

Profile **every Tier 1 and Tier 2 table** in the next step. Tier 3 tables are
noted but profiled only if they appear to be useful join dimensions.

---

## Step 3: Table Profiling

For each Tier 1 and Tier 2 table, capture:

### Structure
```sql
DESCRIBE TABLE <catalog>.<schema>.<table>;
```

### Row counts
```sql
SELECT COUNT(*) AS row_count FROM <catalog>.<schema>.<table>;
```

### Date range (if date columns exist)
```sql
SELECT
  MIN(<date_col>) AS earliest,
  MAX(<date_col>) AS latest,
  COUNT(DISTINCT <date_col>) AS distinct_periods
FROM <catalog>.<schema>.<table>;
```

### Company dimension
```sql
SELECT
  COUNT(DISTINCT <company_col>) AS company_count
FROM <catalog>.<schema>.<table>;
```

### Column cardinality and nulls
```sql
SELECT
  '<column_name>' AS col,
  COUNT(*) AS total_rows,
  COUNT(<column_name>) AS non_null,
  COUNT(DISTINCT <column_name>) AS distinct_values,
  ROUND((COUNT(*) - COUNT(<column_name>)) * 100.0 / COUNT(*), 1) AS null_pct
FROM <catalog>.<schema>.<table>;
```

---

## Step 4: PII Detection

Flag columns that may contain PII. **Record column names only — never output
PII values.**

PII indicator patterns:
- Names: `first_name`, `last_name`, `full_name`, `name`, `employee_name`
- IDs: `ssn`, `social_security`, `national_id`, `tax_id`, `passport`
- Contact: `email`, `phone`, `address`, `postal`, `zip`
- Financial: `bank_account`, `routing_number`, `iban`
- Dates: `birth_date`, `date_of_birth`, `dob`

Document PII columns in the schema map with a `⚠️ PII` marker.

---

## Step 5: Cross-Table Relationships

Discover foreign key relationships between tables:

1. Look for matching column names across tables (e.g. `employee_id` appears
   in both `employees` and `terminations`)
2. Validate relationships with a join test:

```sql
SELECT
  COUNT(DISTINCT a.<join_col>) AS keys_in_left,
  COUNT(DISTINCT b.<join_col>) AS keys_in_right,
  COUNT(DISTINCT CASE WHEN b.<join_col> IS NOT NULL THEN a.<join_col> END) AS matched
FROM <table_a> a
LEFT JOIN <table_b> b ON a.<join_col> = b.<join_col>;
```

3. Classify each relationship: one-to-one, one-to-many, many-to-many

Document all validated relationships in the schema map.

---

## Step 6: Company Index

Build a master company index:

```sql
-- For each table that has a company dimension
SELECT
  <company_col> AS company_id,
  COUNT(*) AS record_count
FROM <table>
GROUP BY <company_col>
ORDER BY record_count DESC;
```

Produce a summary showing:
- Total distinct companies in the dataset
- Record count per company per table
- Companies that appear in all Tier 1 tables vs. partial coverage

---

## Output Format

Write all findings to `output/schema_map.md` using this structure:

```markdown
# Schema Map — Databricks Warehouse
**Generated**: <timestamp>
**Catalogs scanned**: <n>
**Total tables found**: <n>
**Tier 1 (Core HR)**: <n> tables
**Tier 2 (HR-Adjacent)**: <n> tables

---

## Table Inventory

### <catalog>.<schema>.<table_name>
- **Tier**: 1/2/3/0
- **Rows**: <n>
- **Date range**: <earliest> to <latest> (<n> periods)
- **Companies**: <n>
- **PII columns**: ⚠️ <list or "None detected">
- **Key columns**: <list with cardinality>
- **Null rates**: <columns with >10% null rate>
- **Relationships**: → <related tables>

---

## Cross-Table Relationships
<relationship diagram or list>

## Company Index
<company coverage matrix>

## PII Register
<all PII columns across all tables — names only>
```

---

## Query Storage

Save all SQL queries that produce results to `queries/discovery/` with
descriptive filenames:

- `queries/discovery/01_catalog_inventory.sql`
- `queries/discovery/02_table_profiling_<table>.sql`
- `queries/discovery/03_relationship_validation.sql`
- `queries/discovery/04_company_index.sql`

---

## Session 1 Handoff

Write to `output/session_log.md`:

```markdown
## Session 1 Handoff

**Catalogs scanned**: <n>
**Total tables**: <n>
**Tier 1 tables**: <n> — <list>
**Tier 2 tables**: <n> — <list>
**PII columns flagged**: <n>
**Cross-table relationships found**: <n>
**Companies in dataset**: <n>
**Date range**: <earliest> to <latest>
**Key data quality issues**: <list>
**Ready for**: Session 1.5 (Gap Analysis)
```
