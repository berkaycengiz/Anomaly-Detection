import express from 'express';
import { newAnomaly, getAllAnomalies, getAnomaly, patchAnomaly } from '../controllers/anomalies';
import upload from '../middlewares/multer';


export default (router: express.Router) => {
    router.post('/anomaly', upload.single("video"), newAnomaly);
    router.get('/anomalies', getAllAnomalies);
    router.get('/anomaly/:id', getAnomaly);
    router.patch('/anomaly/:id', patchAnomaly);
};