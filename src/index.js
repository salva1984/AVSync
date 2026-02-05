import dotenv from 'dotenv';
import { access } from "fs/promises";
import * as fs from 'node:fs/promises';
import path from "path";
import { chromium } from "playwright";
import terminalImage from 'terminal-image';
import { fileURLToPath } from "url";
import { login } from "./auth/login.js";
import { errors } from "playwright";


export const PROJECT_ROOT = path.resolve(
    path.dirname(fileURLToPath(import.meta.url)),
    ".."
)
const cookiesPath = path.join(PROJECT_ROOT, "cookies.json");
const hasCookies = await fileExists(cookiesPath);

dotenv.config();

const browser = await chromium.launch({ headless: true });

const context = await createContext();

const page = await context.newPage();

await page.goto('https://aulavirtual.espol.edu.ec/');

try {
    await page.waitForSelector(".bienvenidos", { timeout: 5000 })
    hasCookies ? console.log("► Sesion expirada, iniciando sesion") : console.log("► Iniciando sesion");
    await login(page);
} catch (error) {
    if (error instanceof errors.TimeoutError) {
        console.log("► Cookies validas");
    } else {
        console.log(error);
        throw error;
    }
}


async function createContext() {
    if (hasCookies) {
        console.log("► Cookies encontradas");
        return browser.newContext({ storageState: cookiesPath });
    }
    console.log("► No hay cookies");
    return browser.newContext();
}

async function fileExists(path) {
    try {
        await access(path, fs.F_OK);
        return true;
    } catch {
        return false;
    }
}

