const { override, addWebpackPlugin, addBabelPlugins } = require('customize-cra');
const webpack = require('webpack');
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
const CompressionPlugin = require('compression-webpack-plugin');

module.exports = override(
  // Optimiser les imports
  ...addBabelPlugins(
    // Import uniquement ce qui est nécessaire depuis les bibliothèques
    [
      'babel-plugin-import',
      {
        libraryName: 'antd',
        style: true,
      },
      'antd'
    ],
    [
      'babel-plugin-import',
      {
        libraryName: '@mui/material',
        libraryDirectory: '',
        camel2DashComponentName: false,
      },
      'mui-material'
    ],
    [
      'babel-plugin-import',
      {
        libraryName: '@mui/icons-material',
        libraryDirectory: '',
        camel2DashComponentName: false,
      },
      'mui-icons'
    ]
  ),

  // Ajouter plugins webpack
  (config) => {
    // Mode production pour optimisations
    if (process.env.NODE_ENV === 'production') {
      // Compression Gzip
      config.plugins.push(
        new CompressionPlugin({
          algorithm: 'gzip',
          test: /\.(js|css|html|svg)$/,
          threshold: 10240,
          minRatio: 0.8,
        })
      );

      // Compression Brotli
      config.plugins.push(
        new CompressionPlugin({
          algorithm: 'brotliCompress',
          test: /\.(js|css|html|svg)$/,
          compressionOptions: { level: 11 },
          threshold: 10240,
          minRatio: 0.8,
          filename: '[path][base].br',
        })
      );
    }

    // Analyser le bundle (décommenter pour voir les stats)
    // config.plugins.push(
    //   new BundleAnalyzerPlugin({
    //     analyzerMode: 'static',
    //     openAnalyzer: false,
    //   })
    // );

    // Optimisations de split chunks
    config.optimization = {
      ...config.optimization,
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          // Vendors séparés
          defaultVendors: {
            test: /[\\/]node_modules[\\/]/,
            priority: -10,
            reuseExistingChunk: true,
            name(module) {
              // Grouper par package
              const packageName = module.context.match(/[\\/]node_modules[\\/](.*?)([\\/]|$)/)[1];
              
              // Packages lourds dans des chunks séparés
              if (packageName.includes('mui')) return 'vendor-mui';
              if (packageName.includes('antd')) return 'vendor-antd';
              if (packageName.includes('recharts')) return 'vendor-recharts';
              if (packageName.includes('framer-motion')) return 'vendor-framer';
              if (packageName.includes('react')) return 'vendor-react';
              
              return 'vendor-other';
            },
          },
          default: {
            minChunks: 2,
            priority: -20,
            reuseExistingChunk: true,
          },
        },
      },
      // Runtime chunk séparé
      runtimeChunk: 'single',
    };

    // Désactiver source maps en développement pour améliorer les performances
    if (process.env.GENERATE_SOURCEMAP === 'false') {
      config.devtool = false;
    }

    return config;
  }
);
