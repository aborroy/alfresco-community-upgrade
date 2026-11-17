// Generates a Docker Compose environment with alfresco-docker-installer, without prompts.
// Usage: node scripts/gen-env.mjs <installer-dir> <acs-version> <target-dir> [--key=value ...]
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';

const [installerDir, acsVersion, targetDir, ...extra] = process.argv.slice(2);
if (!installerDir || !acsVersion || !targetDir) {
  console.error('Usage: node scripts/gen-env.mjs <installer-dir> <acs-version> <target-dir> [--key=value ...]');
  process.exit(1);
}

const require = createRequire(path.join(path.resolve(installerDir), 'package.json'));
const { createEnv } = await import(require.resolve('yeoman-environment'));

const isNew = ['26.1', '26.2'].includes(acsVersion);
// The official alfresco/ images for 7.4 and later are multi-arch, so the installer's
// arm64 images are not used.
const isArm = false;

const answers = {
  acsVersion,
  arch: isArm,
  ram: '16',
  https: false,
  proxyType: 'nginx',
  searchType: acsVersion === '26.2' ? 'opensearch' : 'alfresco',
  opensearchDashboards: false,
  serverName: 'localhost',
  password: 'admin',
  port: '8080',
  configureHttpIp: false,
  httpBindingIp: '0.0.0.0',
  ftp: false,
  configureFtpIp: false,
  ftpBindingIp: '0.0.0.0',
  mariadb: false,
  crossLocale: true,
  enableContentIndexing: true,
  solrHttpMode: acsVersion.startsWith('6.') || ['7.0'].includes(acsVersion) ? 'http' : 'secret',
  activemq: isNew,
  activeMqCredentials: isNew,
  activeMqUser: 'admin',
  activeMqPassword: 'password',
  smtp: false,
  ldap: false,
  addons: '',
  windows: false,
  startscript: false,
  volumesscript: false
};
for (const arg of extra) {
  const [k, v] = arg.replace(/^--/, '').split('=');
  answers[k] = v;
}

const args = Object.entries(answers).map(([k, v]) => `--${k}=${v}`);
fs.mkdirSync(targetDir, { recursive: true });
const env = createEnv({ cwd: path.resolve(targetDir) });
env.register(path.join(path.resolve(installerDir), 'generators/app/index.js'), { namespace: 'alfresco-docker-installer:app' });
await env.run(['alfresco-docker-installer:app', ...args], { skipInstall: true, force: true });
