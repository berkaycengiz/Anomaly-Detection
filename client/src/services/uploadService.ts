import axios from "axios";

const BASE_URL = import.meta.env.VITE_BASE_API_URL;

export const createAnomaly = async (file: File | null) => {
    const formData = new FormData();

    if(file){
        formData.append('video', file);
    }

    try {
        const response = await axios.post(`${BASE_URL}/anomaly`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
        withCredentials: true,
    });
        console.log('Video uploaded:', response.data);
        return response.data;
    } 
    catch (error: any) {
        throw error.response?.data?.message
    }
};