import express from 'express';
import { newAnomaly, getAllAnomalies, getAnomaly, updateAnomaly } from '../controllers/anomalies';
import upload from '../middlewares/multer';


export default (router: express.Router) => {
    router.post('/anomaly', upload.single("photo"), newAnomaly);
    router.get('/anomalies', getAllAnomalies);
    router.get('/anomaly/:id', getAnomaly);
    router.patch('/anomaly/:id', updateAnomaly);
};