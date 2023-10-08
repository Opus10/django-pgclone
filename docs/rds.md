# Dumping RDS Databases

RDS requires a preparatory step to take place in order to dump the database. This can be handled by writing a pre-dump hook management command like the following:

```python
class Command(BaseCommand):
    def handle(self, *args, **options):
        print_msg(f'Running RDS prep SQL.')
        rds_prep_sql = '''
            CREATE OR REPLACE FUNCTION exec(text)
                returns text language plpgsql volatile AS
                $f$ BEGIN EXECUTE $1; RETURN $1; END; $f$;
            SELECT exec(
                'ALTER TABLE ' || quote_ident(s.nspname)
                || '.' || quote_ident(s.relname) || ' OWNER TO rds_superuser'
            )
            FROM (
                SELECT nspname, relname
                FROM pg_class c JOIN pg_namespace n ON (c.relnamespace = n.oid)
                WHERE nspname in ('tiger','topology') AND
                relkind IN ('r','S','v') ORDER BY relkind = 'S')
            s;
        '''
        with connection.cursor() as cursor:
            cursor.execute(rds_prep_sql)
```

After you write this management command and name it `rds_prep_management_command_name`, edit your `settings.PGCLONE_PRE_DUMP_HOOKS` to enable it by default:

```python
PGCLONE_PRE_DUMP_HOOKS = ["rds_prep_management_command_name"]
```
