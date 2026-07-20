export const REPO_URL = 'https://github.com/Aman-Agnihotri/Project-Nurture';
export const REPO_BRANCH = 'main';
export const DOCS_PATH = 'docs';

export const repositoryDocumentUrl = fileName =>
  `${REPO_URL}/blob/${REPO_BRANCH}/${DOCS_PATH}/${fileName}`;
