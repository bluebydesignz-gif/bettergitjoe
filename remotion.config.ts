import {Config} from '@remotion/cli/config';
import {existsSync} from 'fs';

// Cloud sessions ship a headless Chromium here. Use it if present.
const cloudChrome =
  '/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell';
if (existsSync(cloudChrome)) {
  Config.setBrowserExecutable(cloudChrome);
}
// Software WebGL so Three.js scenes render without a GPU.
Config.setChromiumOpenGlRenderer('swangle');
