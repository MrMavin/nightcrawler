const path = require('path');
const fs = require('fs');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');

// Dynamically discover entry points
function getEntryPoints() {
  const entries = {};
  
  // Recursively find all TSX files anywhere in src
  function findTsxFiles(dir, basePath = '') {
    if (!fs.existsSync(dir)) return;
    
    const files = fs.readdirSync(dir);
    files.forEach(file => {
      const fullPath = path.join(dir, file);
      const stat = fs.statSync(fullPath);
      
      if (stat.isDirectory()) {
        findTsxFiles(fullPath, basePath ? `${basePath}/${file}` : file);
      } else if (file.endsWith('.tsx')) {
        const name = basePath ? `${basePath}/${file.replace('.tsx', '')}` : file.replace('.tsx', '');
        entries[name] = './' + fullPath;
      }
    });
  }
  
  // Find ALL TSX files in src directory recursively
  findTsxFiles('./src');
  
  return entries;
}

// Dynamically create HTML plugins
function getHtmlPlugins() {
  const plugins = [];
  
  // Find all HTML files and match them with TSX files
  function findHtmlFiles(dir, basePath = '') {
    if (!fs.existsSync(dir)) return;
    
    const files = fs.readdirSync(dir);
    files.forEach(file => {
      const fullPath = path.join(dir, file);
      const stat = fs.statSync(fullPath);
      
      if (stat.isDirectory()) {
        findHtmlFiles(fullPath, basePath ? `${basePath}/${file}` : file);
      } else if (file.endsWith('.html')) {
        const name = file.replace('.html', '');
        const chunkName = basePath ? `${basePath}/${name}` : name;
        
        plugins.push(new HtmlWebpackPlugin({
          template: fullPath,
          filename: file,
          chunks: [chunkName],
          inject: 'body'
        }));
      }
    });
  }
  
  findHtmlFiles('./src/components');
  
  return plugins;
}

const entries = getEntryPoints();
const htmlPlugins = getHtmlPlugins();

console.log('📦 Webpack entries:', Object.keys(entries));
console.log('📄 HTML pages:', htmlPlugins.length);

module.exports = {
  mode: process.env.NODE_ENV === 'production' ? 'production' : 'development',
  devtool: process.env.NODE_ENV === 'production' ? false : 'inline-source-map',
  entry: entries,
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].js',
    clean: true
  },
  resolve: {
    extensions: ['.tsx', '.ts', '.js', '.jsx']
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: 'ts-loader',
        exclude: /node_modules/
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader']
      }
    ]
  },
  plugins: [
    ...htmlPlugins,
    new CopyWebpackPlugin({
      patterns: [
        { from: 'manifest.json', to: 'manifest.json' },
        { 
          from: 'dist/styles.css', 
          to: 'styles.css',
          noErrorOnMissing: true 
        },
        {
          from: 'assets/*.png',
          to: '[name][ext]',
          noErrorOnMissing: true
        }
      ]
    })
  ],
  optimization: {
    splitChunks: false, // Important for Chrome extensions
    runtimeChunk: false // Disable runtime chunk for Chrome extensions
  }
};