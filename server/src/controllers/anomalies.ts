import express from 'express';
import {getAnomalyById, getAnomalies, createAnomaly, updateAnomaly} from '../db/anomalies';
import { uploadFromBuffer } from '../helpers/cloudinaryHelper';
import { UploadApiOptions } from 'cloudinary';
import axios from 'axios';

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
        let videoUrl = "";
        let videoName = "";

        if (req.file) {
            videoName = req.file.originalname;
            const options: UploadApiOptions = {folder: 'anomaly-videos', resource_type: 'video'};
            const result = await uploadFromBuffer(req.file.buffer, options);
            videoUrl = result.secure_url;
        }
        else {
            return res.status(400).json({ message: "Supported formats: mp4."});
        }

        const anomaly = await createAnomaly({
            originalUrl: videoUrl,
            videoName: videoName,
        });

        axios.post(`${process.env.FASTAPI_URL}/analyze`, {
            id: anomaly._id,
            videoUrl: videoUrl
        })
        .then(() => console.log(`FastAPI analysis started for: ${anomaly._id}`))
        .catch(err => console.error("FastAPI Error:", err.message));

        return res.status(200).json(anomaly);
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

export const patchAnomaly = async (req: express.Request, res: express.Response): Promise<any> => {
    try{
        const {id} = req.params;
        const values = req.body;

        const updatedRecord = await updateAnomaly(id, values);

        if (!updatedRecord) {
            return res.status(404).json({ message: "Anomaly not found." });
        }

        return res.status(200).json(updatedRecord);
    }
    catch(error){
        console.log(error);
        return res.sendStatus(400);
    }
};