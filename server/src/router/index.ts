import express from 'express';
import anomaly from './anomaly';

const router = express.Router();

export default(): express.Router => {
    anomaly(router);
    
    return router;
};