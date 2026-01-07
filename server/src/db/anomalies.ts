import mongoose from "mongoose";
const { Schema } = mongoose;

const AnomalySchema = new mongoose.Schema({
    originalUrl: {type: String, required: true},
    videoName: {type: String, required: true},
    isAnomaly: {type: Boolean, default: null},
    accuracy: {type: Number, default: null},
}, {timestamps: true});

export const AnomalyModel = mongoose.model('Anomaly', AnomalySchema);

export const getAnomalies = () => AnomalyModel.find().sort({ createdAt: -1 });
export const createAnomaly = (values: Record<string, any>) => new AnomalyModel(values).save().then((anomaly) => anomaly.toObject());
export const updateAnomaly = (id: string, values: Record<string, any>) => AnomalyModel.findByIdAndUpdate(id, values, { new: true });
export const getAnomalyById = (id: string) => AnomalyModel.findById(id);