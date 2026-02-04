import { chromium } from "playwright";
import terminalImage from 'terminal-image';
import readline from 'node:readline';

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
});

export async function login() {

    let numeroAutenthicator;

    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();

    await page.goto('https://aulavirtual.espol.edu.ec/login/openid_connect');
    try {
        await page.waitForURL('https://sts.espol.edu.ec/adfs/ls/**');

        await page.getByPlaceholder('usuario@espol.edu.ec').fill(process.env.EMAIL);

        //password cambia dependiendo de el idioma
        await page.locator('#passwordInput').fill(process.env.PASSWORD);
        await page.locator('#submitButton').click();

        await page.waitForURL('https://login.microsoftonline.com/login.srf');
        
        // confiar en espol.edu.ec
        await page.locator('#idSIButton9').click();

        await page.waitForURL('https://login.microsoftonline.com/appverify');
        // esperamos esa animacion
        await page.waitForTimeout(2000);
        const buffer = await page.locator('.display-sign-container').screenshot();
        // muestra el numero de auth en consola
        console.log(await terminalImage.buffer(buffer));

        await page.getByRole('input', { value: 'Yes' }).click();
        console.log(page.url());

    } catch (error) {
        const buffer = await page.screenshot({ path: 'error.png', fullPage: true });
        console.log(await terminalImage.buffer(buffer));
        throw error;
    }






}