const slugBase = name => String(name || '')
  .normalize('NFKD')
  .replace(/\p{M}/gu, '')
  .replaceAll('&', ' and ')
  .toLowerCase()
  .replace(/[^\p{L}\p{N}]+/gu, '-')
  .replace(/^-+|-+$/g, '');

export const toSlug = name => slugBase(name) || 'unnamed';

const uniqueSlug = (name, used) => {
  const base = toSlug(name);
  const count = used.get(base) || 0;
  used.set(base, count + 1);
  return count ? `${base}-${count + 1}` : base;
};

/** Build reversible state and district lookups without inferring names from URLs. */
export const buildSlugLookup = records => {
  const stateBySlug = new Map();
  const districtBySlug = new Map();
  const stateSlugs = new Map();
  const districtUsesByState = new Map();
  const sorted = [...(records || [])].sort((left, right) => `${left.state_name}|${left.district_name}`.localeCompare(`${right.state_name}|${right.district_name}`));

  sorted.forEach(record => {
    const stateName = record.state_name || '';
    if (!stateSlugs.has(stateName)) {
      const stateSlug = uniqueSlug(stateName, new Map([...stateSlugs.values()].map(value => [value, 1])));
      stateSlugs.set(stateName, stateSlug);
      stateBySlug.set(stateSlug, stateName);
      districtUsesByState.set(stateSlug, new Map());
    }
    const stateSlug = stateSlugs.get(stateName);
    const districtSlug = uniqueSlug(record.district_name, districtUsesByState.get(stateSlug));
    districtBySlug.set(`${stateSlug}/${districtSlug}`, record);
  });
  return { stateBySlug, districtBySlug, stateSlugs };
};
