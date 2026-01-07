import express from 'express';
import http from 'http';
import bodyParser from 'body-parser';
import cookieParser from 'cookie-parser';
import compression from 'compression';
import cors from 'cors';
import mongoose from 'mongoose';
import dotenv from 'dotenv';
import router from './router';
import { cloudinary } from './config/cloudinaryConfig'; 

dotenv.config();

const app = express();

app.use(cors({
    origin: process.env.FRONTEND_URL,
    credentials: true,
}));

app.use(compression());
app.use(cookieParser());
app.use(bodyParser.json());

const server = http.createServer(app);
const port = process.env.PORT;

server.listen(Number(port), "0.0.0.0", () => {
    console.log('Server is running on http://localhost:' + port + '/');
});

const MONGO_URL = process.env.DATABASE_URL;

mongoose.Promise = Promise;
mongoose.connect(MONGO_URL);
mongoose.connection.on('error', (error: Error) => console.log(error));

module.exports = cloudinary;



app.use('/', router());