// headless Chromium with software WebGL, as the pictures here are made
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
export async function browser() {
  const { chromium } = require('playwright');
  return chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
}
