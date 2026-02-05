import terminalImage from 'terminal-image';

export async function login(page) {

    let numeroAutenthicator;

    await page.goto('https://aulavirtual.espol.edu.ec/login/openid_connect');
    try {
        await page.waitForURL('https://sts.espol.edu.ec/adfs/ls/**');

        //password cambia dependiendo de el idioma
        await page.getByPlaceholder('usuario@espol.edu.ec').fill(process.env.EMAIL);
        await page.locator('#passwordInput').fill(process.env.PASSWORD);
        await page.locator('#submitButton').click();

        await page.waitForURL('https://login.microsoftonline.com/login.srf');

        // confiar en espol.edu.ec
        await page.locator('#idSIButton9').click();

        await page.waitForURL('https://login.microsoftonline.com/appverify');
        // esperamos esa animacion
        await page.waitForTimeout(2000);

        // muestra el numero de auth en consola
        const buffer = await page.locator('.display-sign-container').screenshot();
        console.log(await terminalImage.buffer(buffer));

        // guardar sesion -> si
        await page.locator('#idSIButton9').click();
        console.log(page.url());

       
        await page.context().storageState({ path:'cookies.json' })
        console.log('Cookies saved!');

        return page;

    } catch (error) {
        const buffer = await page.screenshot({ path: 'error.png', fullPage: true });
        console.log(await terminalImage.buffer(buffer));
        throw error;
    }

}