import axios from "axios";

const BASE_URL = import.meta.env.VITE_BASE_API_URL;

export const getAnomalies = async () => {
    try {
        const response = await axios.get(`${BASE_URL}/anomalies`);
        return response.data;
    } 
    catch (error: any) {
        throw error.response?.data?.message || "An unknown error occured!";
    }
};