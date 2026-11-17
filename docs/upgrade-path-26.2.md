# Upgrade path to Alfresco Community 26.2

This page explains how to upgrade an existing Alfresco Community Edition installation to 26.2 with the fewest steps. It lists every manual operation you must do on the way, including the search re-index.

Every path marked as rehearsed was tested with a real repository: data created on an old release, upgraded, and then checked (users, sites, folders, version history, comments, tags, properties, content checksums, new uploads, PDF renditions and full-text search). The test project is public, so you can repeat the rehearsal with your own data: https://github.com/aborroy/alfresco-community-upgrade

## Upgrade path

| Current version | Path to 26.2 | Steps | Rehearsed |
| --- | --- | --- | --- |
| 26.1.x | 26.1 -> 26.2 | 1 | Yes (26.1.0) |
| 25.x | 25.x -> 26.2 | 1 | Yes (25.3.0) |
| 23.x | 23.x -> 26.2 | 1 | Yes (23.4.1) |
| 7.x | 7.x -> 26.2. Apply the latest 7.4 patch first if you are on 7.4 | 1 | Yes (7.4.2) |
| 6.x | 6.x -> 26.2 | 1 | Yes (6.1.2) |
| 5.2 | 5.2 -> 7.4.2 -> 26.2 | 2 | No |

For 5.2, the step to 7.4 is the documented upgrade path for that release. The 5.2 path was not rehearsed, because there is no 5.2 Docker image to build the test on.

In all rehearsals the repository upgraded its database schema on the first start. No version required an intermediate stop.

## Before you start

- Back up the database, the content store (`alf_data`) and your configuration (`alfresco-global.properties`, the `extension` folders, AMPs and JARs).
- Rehearse the upgrade on a copy of your production data before you touch production.
- Check your add-ons first (see "Check your add-ons" below). On most old installations this is the largest part of the work.
- Plan a maintenance window for the search re-index, or keep Solr running as a rollback target during the migration (see "Search: initial index").
- Install 26.2 in a new location. Do not upgrade binaries or configuration in place, so the old system stays ready to restart.

## What changes on the way

Versions read from the official Community Docker images.

| Version | Java | Tomcat | Servlet API | Search |
| --- | --- | --- | --- | --- |
| 6.1.2 | 11 | 8.5 | `javax` | Search Services 1.x (Solr 6) |
| 7.4.2 | 17 | 9 | `javax` | Search Services 2.0 |
| 23.4.1 | 17 | 10.1 | `jakarta` | Search Services 2.0 |
| 25.3.0 | 17 | 10.1 | `jakarta` | Search Services 2.0 |
| 26.1.0 | 21 | 11 | `jakarta` | Search Services 2.0 |
| 26.2.0 | 21 | 11 | `jakarta` | Alfresco Search Community (OpenSearch or Elasticsearch) |

Breaking changes to review in the 26.2 release notes:

- Alfresco Search Services (Solr) is no longer supported. Use Alfresco Search Community with OpenSearch or Elasticsearch.
- Java 21 and Tomcat 11 (from 26.1).
- ActiveMQ 6 with authentication: the broker needs a user name and password.
- v1 events are disabled. Check any integration that consumes repository events.
- Share has its own patch versions (Share 26.2.1 for repository 26.2.0). Upgrade Share together with the repository.

## Upgrade steps

### 1. Stop the old system and take the data

Stop the repository, then dump the database and copy the content store. Example for PostgreSQL:

```bash
pg_dump -U alfresco -Fc alfresco > alfresco.dump
cp -a /path/to/alf_data /backup/alf_data
```

### 2. Install 26.2 in a new location

Use the distribution ZIP, Docker Compose or Helm. Check the Supported Platforms page for the database, message broker and search versions.

### 3. Restore the database

Restore into the database server for 26.2. A dump can move to a newer PostgreSQL major version this way:

```bash
pg_restore -U alfresco -d alfresco --no-owner alfresco.dump
```

The message `schema "public" already exists` is expected and harmless.

Point `dir.root` at the copied content store.

### 4. Port the configuration

Copy only your overrides into the new `alfresco-global.properties`. Do not copy old default files over the new ones. Then add the 26.2 settings:

```properties
index.subsystem.name=elasticsearch
elasticsearch.host=opensearch
elasticsearch.port=9200
elasticsearch.createIndexIfNotExists=true

messaging.broker.url=failover:(nio://activemq:61616)?timeout=3000&jms.useCompression=true
messaging.broker.username=<user>
messaging.broker.password=<password>
```

Remove the Solr settings (`solr.*`, `solr6` subsystem), unless you keep Solr as a rollback target during the migration.

If you have a custom `log4j.properties` file (Log4j 1 format), convert it to Log4j2 (see the "Log4j2 migration guide" in the Community documentation).

### 5. Install your add-ons

Install only add-ons built for 26.2: Java 21 and the `jakarta` servlet API. See "Check your add-ons".

### 6. Start the repository

On the first start the repository upgrades the database schema. Check the log for a line like this one:

```text
Alfresco Content Services started (Community). Current version: 26.2.0 (...) schema 21,100. Originally installed version: 6.1.2 (...) schema 13,001.
```

### 7. Build the search index

This step is required. See the next section.

### 8. Validate

See "Validate the upgrade".

## Search: initial index

There is no data migration from Solr to OpenSearch or Elasticsearch. The index is always built again from the repository.

The batch indexer does not index existing content by default. On its first start it only indexes changes from the last 10 minutes. In addition, with the default `maxGapAge` of 24 hours, a starting point older than one day is skipped without an error. In a rehearsal with two-year-old content and default settings, the indexer reported itself up to date while only 13 of 869 nodes were in the index.

To index the existing content, seed the indexer cursor at the first repository transaction and remove the gap limit during the initial index. The full explanation is in the Alfresco Search Community guide, section "Migrating from Solr to OpenSearch": https://community.hyland.com/discussion/500354

1. Start 26.2 with the `elasticsearch` subsystem, then start the batch indexer once, so it creates its state index. Then stop the batch indexer.

2. Find the first transaction time (milliseconds) and subtract one minute:

   ```bash
   psql -U alfresco -tAc "select min(commit_time_ms) - 60000 from alf_transaction"
   ```

3. Write the cursor (`$OS` is the OpenSearch or Elasticsearch URL):

   ```bash
   curl -X PUT "$OS/alfresco-reindex-state/_doc/reindexByDate-watermark?refresh=true" \
     -H 'Content-Type: application/json' \
     -d '{"schemaVersion":1,"lastSuccessfulToTimeEpochMs":<value from step 2>}'
   ```

4. Start the batch indexer with these settings for the initial index:

   ```properties
   ALFRESCO_REINDEX_CONTINUOUS_MAXGAPAGE=0
   ALFRESCO_REINDEX_CONTINUOUS_MAXWINDOW=7d
   ```

   The indexer walks the calendar in windows of `MAXWINDOW`, even through periods without changes, so a larger window makes the initial index much faster on repositories with years of history. In the rehearsal, two years of history took 114 seconds with 7-day windows.

5. Follow the progress. The cursor alone is not enough: compare the number of documents in the index with the number of nodes in the repository.

   ```bash
   # cursor position
   curl -s "$OS/alfresco-reindex-state/_doc/reindexByDate-watermark"
   # documents in the index
   curl -s "$OS/alfresco/_count"
   # nodes in the repository
   psql -U alfresco -tAc "select count(*) from alf_node n join alf_store s on s.id = n.store_id where s.protocol = 'workspace' and s.identifier = 'SpacesStore'"
   # items that could not be indexed
   curl -s "$OS/alfresco-reindex-dead-letter/_search?size=20&expand_wildcards=all"
   ```

   The initial index is complete when the cursor follows the current time, the document count is close to the node count, and the dead-letter index is empty or understood.

6. Restart the batch indexer with the steady-state settings (remove the two settings from step 4).

Notes:

- Search results are incomplete until the initial index finishes. Use a maintenance window, or keep Solr as a rollback target: set `index.subsystem.name=elasticsearch` and `search.solrTrackingSupport.enabled=true`, so Solr keeps tracking while OpenSearch catches up.
- Alfresco Search Community has no archive index for deleted nodes. Test any application that searches deleted content.

## Upgrading from 5.2

1. If 5.2 still uses Solr 4, move to Alfresco Search Services before you upgrade the repository to 7.4.
2. Upgrade 5.2 to 7.4.2 (the latest 7.4 patch) and start it once, so the database schema is upgraded.
3. Upgrade 7.4.2 to 26.2 with the steps on this page.

This path was not rehearsed.

## Check your add-ons

An add-on built for an old version can stop the repository or Share from starting on 26.2. Check each one against three things:

1. **Java version.** The add-on must not use a newer Java than the target. Java 11 classes run on Java 21; Java 21 classes do not run on Java 17. Class file versions: 55 = Java 11, 61 = Java 17, 65 = Java 21.
2. **Servlet API.** From 23.x, Tomcat uses `jakarta.*`. An add-on that uses `javax.servlet` (or other `javax` Jakarta EE packages) must be rebuilt for `jakarta`. In the rehearsal, a small add-on with a `javax.servlet.Filter` bean stopped the 26.2 repository from starting (`NoClassDefFoundError: javax/servlet/Filter`); the same add-on built for `jakarta` loaded.
3. **Libraries and beans.** Libraries bundled in an AMP can conflict with the libraries in the 26.2 WAR, and an add-on can overwrite repository beans or use internal classes that changed.

Use the Alfresco Extension Inspector (https://github.com/Alfresco/alfresco-extension-inspector) for items 2 and 3:

```bash
java -jar alfresco-extension-inspector-2.8.0.jar my-addon.amp --target-version=26.2.0
```

The test project adds three things for Community users:

- Inventories built from the Community repository and Share images. The inventories bundled with the Inspector are built from a different WAR.
- The servlet, JSP and EL APIs that Tomcat provides are added to each inventory. Without them the Inspector guesses `javax` or `jakarta` from the mail library in the WAR, and on Share that guess is wrong.
- A Java version check, which the Inspector does not do.

```bash
scripts/build-inventories.sh alfresco-extension-inspector-2.8.0.jar
scripts/addon-check.sh alfresco-extension-inspector-2.8.0.jar my-addon.amp 26.2
```

Check Share add-ons against the Share inventory, and repository add-ons against the repository inventory.

How to read the findings:

| Finding | Meaning for the upgrade |
| --- | --- |
| Java version | Blocker. Rebuild the add-on for the target Java. |
| `JAKARTA_MIGRATION_CONFLICT` | Blocker, unless the add-on ships both `javax` and `jakarta` classes (a dual build). A dual build is flagged on every version; check the add-on documentation. |
| `CLASSPATH_CONFLICT` | Risk. The add-on bundles a library that is also in the WAR. Remove the bundled copy or check that both versions are the same. |
| `BEAN_OVERWRITE`, `FILE_OVERWRITE` | Risk. The add-on replaces a repository bean or file. Check that the original did not change. |
| `ALFRESCO_INTERNAL_USAGE`, `WAR_LIBRARY_USAGE`, `BEAN_RESTRICTED_CLASS` | Information. These also appear on the version the add-on was built for. Test the related features. |

Example results for add-ons from the alfresco-docker-installer catalog, checked against 26.2: eSign Cert 1.8.4 has `jakarta_migration` findings from 23.x on and needs a new build; OOTBee Support Tools 1.2.3.0 is a dual build; JavaScript Console, PDF Toolkit, Share Site Creators and Share Site Space Templates have no blockers.

## Validate the upgrade

- Users can log in, and sites, folders and documents are where they were.
- Version history is complete and old versions open.
- Comments, tags and custom properties are kept.
- Content opens and is the same as before (compare checksums for a sample).
- New documents can be uploaded.
- Renditions work: request a PDF rendition and a thumbnail of a new document.
- Full-text search finds old content and new content.

## Known issues

- Right after startup, a rendition request can fail with HTTP 404 for a few seconds, until the repository has loaded the transform configuration. Try again after some seconds.
