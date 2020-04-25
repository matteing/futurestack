const withPlugins = require("next-compose-plugins");
const nextEnv = require("next-env");
const dotenvLoad = require("dotenv-load");
const path = require("path");
const webpack = require("webpack");

dotenvLoad();

const nextConfig = {
  webpack: (config) => {
    config.resolve.alias["~"] = path.resolve(__dirname);
    return config;
  },
};

module.exports = withPlugins(
  [
    nextEnv({
      staticPrefix: "STATIC_",
      publicPrefix: "PUBLIC_",
    }),
  ],
  nextConfig
);
