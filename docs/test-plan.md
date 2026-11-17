# Test plan

Goal: find the upgrade path to Alfresco Community 26.2 with the fewest steps, and prove it with real data.

## Method

- Environments are generated with alfresco-docker-installer (`scripts/gen-env.mjs`), one per version, in `test/envs/<version>`.
- The test data is created once on 6.1.2 (`test/upgrade.sh seed`). Every other source version is produced by upgrading that data, so each step starts from a repository that was really created on an older release.
- Each step restores a snapshot (PostgreSQL dump and `alf_data`) into a clean environment of the next version. The database moves to the PostgreSQL version of that environment with `pg_dump` and `pg_restore`.
- The search index always starts empty. On Solr versions it is rebuilt by Solr. On 26.2 it is built with the initial-index procedure (`test/upgrade.sh reindex`).
- There is no Community 5.2 Docker image, so the data starts on 6.1.2.

## Steps

| Step | Purpose |
| --- | --- |
| 6.1.2 baseline | Create the test data |
| 6.1.2 -> 7.4.2 | Source for 7.x |
| 7.4.2 -> 23.4.1 | Source for 23.x |
| 7.4.2 -> 25.3.0 | Source for 25.x |
| 7.4.2 -> 26.1.0 | Source for 26.1 |
| 6.1.2, 7.4.2, 23.4.1, 25.3.0, 26.1.0 -> 26.2.0 | One step from every source version |
| 6.1.2 data moved back 2 years -> 26.2.0, default settings | Shows that old history is skipped without the procedure |
| 6.1.2 data moved back 2 years -> 26.2.0, initial-index procedure | Shows that the procedure indexes old history |

## Checks after each step

- The repository starts and upgrades the schema (log line `Current version ... Originally installed version`).
- Site, user, login, folder, documents, version history, comments, tags and properties.
- Content checksums for the latest version, an old version and a binary file.
- Upload of a new document, and a PDF rendition of it (the result starts with `%PDF`).
- Full-text search for a word in old content and a word in the new document.
- On 26.2: the initial index reaches the present, covers at least 95% of the repository nodes, and has no dead letters.
- Long steps are watched all the time: a step fails at once if OpenSearch, the batch indexer or Solr stops, or if indexing makes no progress for 90 seconds.

## Other checks

- Share and Content App on an upgraded 26.2 (`test/smoke-ui.sh`): login, site dashboard, document library, thumbnail.
- A probe extension built for `javax` and for `jakarta`, deployed on 26.2 (`test/extension-check/run.sh`).
- Add-ons from the alfresco-docker-installer catalog checked against every version (`test/addon-matrix.sh`).

## Commands

```bash
BATCH_INDEXER_TAG=5.9.0 test/run-matrix.sh
test/smoke-ui.sh 26.2 <label>
test/extension-check/run.sh javax
test/extension-check/run.sh jakarta
test/addon-matrix.sh alfresco-extension-inspector-2.8.0.jar test/addons 6.1 7.4 23.4 25.3 26.1 26.2
```
