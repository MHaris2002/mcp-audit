export const RULE_INFO = [
  { sev: "high", name: "hardcoded_secret", desc: "Credentials written as literal values instead of environment variable references." },
  { sev: "high", name: "insecure_transport", desc: "Remote server URLs using unencrypted http:// instead of https://." },
  { sev: "high", name: "dangerous_flag", desc: "Flags that disable normal safety or permission prompts." },
  { sev: "high", name: "possible_typosquat", desc: "A package name suspiciously close to a known official one." },
  { sev: "medium", name: "broad_filesystem_access", desc: "Servers granted access to broad roots instead of a specific folder." },
  { sev: "medium", name: "shell_metacharacters", desc: "Arguments containing shell metacharacters worth a manual check." },
  { sev: "low", name: "unpinned_version", desc: "Packages installed with @latest instead of a pinned version." },
  { sev: "info", name: "unverified_package", desc: "A package not present in the known-server registry." },
];
