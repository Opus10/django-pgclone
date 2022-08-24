# Changelog
## 2.0.0 (2022-08-24)
### Api-Break
  - Upgrade configuration hierarchy, add multi-db support, and change dump key format [Wes Kendall, 5edeeb8]

    ``django-pgclone`` has ``settings.PGCLONE_CONFIGS`` to support re-usable command
    options. Dump keys were changed to capture the config and also contain a configurable
    database instance to better distinguish different databases.

    Multi-database setups are fully supported.

    Docs were revamped and overview all settings and configuration possibilities.

    Instructions for migrating to version 2 are in the "Frequently Asked Questions" section of
    the docs.

## 1.1.0 (2022-08-21)
### Feature
  - Removed dependency on ``django-pgconnection`` [Wes Kendall, 5047031]

    The routing functionality of ``django-pgconnection`` was replaced by
    Django's built-in execution hooks.

    Users no longer have to wrap ``settings.DATABASES`` with
    ``django-pgconnection``.

## 1.0.5 (2022-08-20)
### Trivial
  - Updated with latest Django template [Wes Kendall, 5ab9ddd]

## 1.0.4 (2022-08-20)
### Trivial
  - Fix release note rendering and don't package tests [Wes Kendall, 5621de7]

## 1.0.3 (2022-07-31)
### Trivial
  - Updated with latest Django template, fixing doc builds [Wes Kendall, 32a5eea]

## 1.0.2 (2021-06-15)
### Trivial
  - Updated to latest Django template [Wes Kendall, cf4deaf]

## 1.0.1 (2020-06-28)
### Trivial
  - Fixed minor documentation typos [Wes Kendall, 68cb863]

## 1.0.0 (2020-06-28)
### Api-Break
  - Initial release of django-pgclone [Wes Kendall, b8419ce]

    ``django-pgclone`` provides management commands for dumping and restoring
    Postgres databases. Users can configure local or S3 storage backends,
    and users may also configure hooks and other processes that happen during
    the dump/restore process.

