import sharp from 'sharp';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { existsSync, mkdirSync } from 'fs';

// Get __dirname equivalent in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const sizes = [72, 96, 128, 144, 152, 192, 384, 512];
const iconDirectory = join(__dirname, '../public/icons');

// Create icons directory if it doesn't exist
if (!existsSync(iconDirectory)) {
  mkdirSync(iconDirectory, { recursive: true });
}

// Base icon path - you'll need to provide a high-resolution source icon
const sourceIcon = join(__dirname, '../src/assets/logo.png');

// Generate icons for each size
sizes.forEach(size => {
  sharp(sourceIcon)
    .resize(size, size)
    .toFile(join(iconDirectory, `icon-${size}x${size}.png`))
    .then(info => {
      console.log(`Generated ${size}x${size} icon`);
    })
    .catch(err => {
      console.error(`Error generating ${size}x${size} icon:`, err);
    });
}); 