import express from 'express';
import {getAnomalyById, getAnomalies, createAnomaly} from '../db/anomalies';
import { uploadFromBuffer } from '../helpers/cloudinaryHelper';

export const getAnomaly = async (req: express.Request, res: express.Response): Promise<any> => {
    try{
        const {id} = req.params;

        const anomaly = await getAnomalyById(id);

        return res.json(anomaly);
    }
    catch(error){
        console.log(error);
        return res.sendStatus(400);
    }
}

export const newAnomaly = async (req: express.Request, res: express.Response): Promise<any> => {
    try{
        let photoUrl = "";

        if (req.file) {
            const options = {folder: 'anomaly-pics'}
            const result = await uploadFromBuffer(req.file.buffer, options);
            photoUrl = result.secure_url;
        }
        else {
            return res.status(400).json({ message: "Supported formats: PNG, JPG, JPEG, BMP."});
        }

        const post = await createAnomaly({
            originalUrl: photoUrl,
          });

        return res.status(200).json(post);
    }
    catch(error){
        console.log(error);
        return res.sendStatus(400);
    }
};

export const getAllAnomalies = async (req: express.Request, res: express.Response): Promise<any> => {
    try{
        const posts = await getAnomalies();

        return res.status(200).json(posts);
    }
    catch(error){
        console.log(error);
        return res.sendStatus(400);
    }
};

export const updateAnomaly = async (req: express.Request, res: express.Response): Promise<any> => {
    try{
        const {id} = req.params;
        const { processedUrl, isAnomaly } = req.body;

        const anomaly = await getAnomalyById(id);

        if (!anomaly) {
            return res.status(404).json({ message: "Record not found." });
        }

        if (processedUrl !== undefined) {
            anomaly.processedUrl = processedUrl;
        }

        if (isAnomaly !== undefined) {
            anomaly.isAnomaly = isAnomaly;
        }

        await anomaly.save();
        
        return res.status(200).json(anomaly).end();
    }
    catch(error){
        console.log(error);
        return res.sendStatus(400);
    }
};