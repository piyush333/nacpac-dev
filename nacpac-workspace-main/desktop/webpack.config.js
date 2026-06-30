const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
  target: 'web',
  entry:  './src/index.tsx',
  output: {
    path:     path.resolve(__dirname),
    filename: 'bundle.js',
  },
  resolve: {
    extensions: ['.tsx', '.ts', '.js'],
    alias: {
      '@shared': path.resolve(__dirname, '../shared'),
    },
    fallback: {
      assert:  false,
      buffer:  false,
      crypto:  false,
      http:    false,
      https:   false,
      os:      false,
      path:    false,
      stream:  false,
      url:     false,
      util:    false,
      zlib:    false,
    },
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use:  'ts-loader',
        exclude: /node_modules/,
      },
      {
        test: /\.css$/,
        use:  [MiniCssExtractPlugin.loader, 'css-loader'],
      },
    ],
  },
  plugins: [
    new MiniCssExtractPlugin({ filename: 'styles.css' }),
  ],
};
