import express from 'express';
import {getAnomalyById, getAnomalies, createAnomaly, updateAnomaly } from '../db/anomalies';
import { uploadFromBuffer } from '../helpers/cloudinaryHelper';
import { extractPublicIdFromUrl } from '../helpers/cloudinaryURLHelper';
import { cloudinary } from '../config/cloudinaryConfig';


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
        if (!req.file) {
            return res.status(400).json({ message: "Supported formats: PNG, JPG, JPEG, BMP."});
        }

        let photoUrl = "";

        if (req.file) {
            const options = {folder: 'anomaly-pics'}
            const result = await uploadFromBuffer(req.file.buffer, options);
            photoUrl = result.secure_url;
        }

        const post = await createAnomaly({
            photo: photoUrl,
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

export const updatePost = async (req: express.Request, res: express.Response): Promise<any> => {
    try{
        const {id} = req.params;

        const anomaly = await getAnomalyById(id);

        if(){

        }

        else{
            return res.status(400).json({ message: "The description is already the same." });
        }

        await post.save();
        
        return res.status(200).json(post).end();
    }
    catch(error){
        console.log(error);
        return res.sendStatus(400);
    }
};