import { chromium } from "playwright";
import terminalImage from 'terminal-image';
import readline from 'node:readline';

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
});

export async function login() {

    let numeroAutenthicator;

    const browser = await chromium.launch({ headless: false });
    const page = await browser.newPage();

    await page.goto('https://aulavirtual.espol.edu.ec/login/openid_connect');

    await page.getByPlaceholder('usuario@espol.edu.ec').fill(process.env.EMAIL);
    await page.getByPlaceholder('Password').fill(process.env.PASSWORD);
    await page.getByRole('button', { name: 'Sign in' }).click();

    await page.waitForURL('https://login.microsoftonline.com/login.srf');
    await page.getByRole('button', { name: 'Continue' }).click();

    await page.waitForURL('https://login.microsoftonline.com/appverify');
    // esperamos esa animacion
    await page.waitForTimeout(2000);
    const buffer = await page.locator('.display-sign-container').screenshot();
    // muestra el numero de auth en consola
    console.log(await terminalImage.buffer(buffer));

    await page.getByRole('input', { value: 'Yes' }).click();
    console.log(page.url());





}