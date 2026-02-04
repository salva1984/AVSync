import { login } from "./auth/login.js";
import dotenv from 'dotenv';

dotenv.config();

await login();