export const extractPublicIdFromUrl = (url: string): string | null => {
    const matches = url.match(/\/upload\/(?:v\d+\/)?(.+)\.(jpg|jpeg|png|webp|gif)$/i);
    if (matches && matches[1]) {
        return matches[1];
    }
    return null;
};