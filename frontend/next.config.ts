// next.config.js
module.exports = {
  reactStrictMode: true,
  output: 'standalone',  // Optional, improves server performance and supports standalone build
  devIndicators: {
    autoPrerender: false,
  },
};
