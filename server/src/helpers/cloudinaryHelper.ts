import { UploadApiErrorResponse, UploadApiOptions, UploadApiResponse } from "cloudinary";
import { cloudinary } from "../config/cloudinaryConfig";
import streamifier from 'streamifier';

export const uploadFromBuffer = (buffer: Buffer, options: UploadApiOptions): Promise<UploadApiResponse> => {
    return new Promise((resolve, reject) => {
      const cld_upload_stream = cloudinary.uploader.upload_stream(
        options,
        (error: UploadApiErrorResponse | undefined, result: UploadApiResponse | undefined) => {
            if (result) {
            resolve(result);
            } 
            else {
            reject(error || new Error('Cloudinary upload failed.'));
            }
        }
        );
        streamifier.createReadStream(buffer).pipe(cld_upload_stream);
    });
};