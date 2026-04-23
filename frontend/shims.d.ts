declare module 'eslint-plugin-oxlint' {
  const pluginOxlint: {
    buildFromOxlintConfigFile: (configFilePath: string) => unknown[]
  }

  export default pluginOxlint
}
