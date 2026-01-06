import React, { useState, useRef } from "react";
import { Sidebar } from "../layouts/Sidebar";
import { animate, AnimatePresence, motion } from "framer-motion";
import { FaUpload } from "react-icons/fa6";
import NavigationButton from "../components/NavigationButton";
import { IoIosArrowForward } from "react-icons/io";
import SubmitButton from "../components/SubmitButton";
import { AiOutlineLoading3Quarters } from "react-icons/ai";

const Home: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'CHECK' | 'HISTORY'>('CHECK');
  const [isSnapping, setIsSnapping] = useState(true);
  const [previewVideo, setPreviewVideo] = useState<string | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [activeCard, setActiveCard] = useState<1 | 2>(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const isNavigating = useRef(false);

  const containerRef = useRef<HTMLDivElement>(null);
  const checkRef = useRef<HTMLDivElement>(null);
  const historyRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleNavigate = (target: 'CHECK' | 'HISTORY') => {
    isNavigating.current = true;
    const targetRef = target === 'CHECK' ? checkRef : historyRef;
    const container = containerRef.current;

    if (container && targetRef.current) {
      setIsSnapping(false);

      const top = targetRef.current.offsetTop;

      animate(container.scrollTop, top, {
        type: "tween",
        duration: 0.8,
        ease: "easeInOut",
        onUpdate: (latest) => {
          container.scrollTop = latest;
        },
        onComplete: () => {
          setIsSnapping(true);
          setTimeout(() => {
            isNavigating.current = false;
          }, 100);
        }
      });
    }
    setActiveTab(target);
  };

  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    if (isNavigating.current) return;

    const { scrollTop, offsetHeight } = e.currentTarget;
    if (scrollTop > offsetHeight / 2) {
      setActiveTab('HISTORY');
    } else {
      setActiveTab('CHECK');
    }
  };

  const generateVideoThumbnail = (file: File): Promise<string> => {
    return new Promise((resolve) => {
      const canvas = document.createElement("canvas");
      const video = document.createElement("video");
      video.autoplay = true;
      video.muted = true;
      video.src = URL.createObjectURL(file);

      video.onloadeddata = () => {
        let ctx = canvas.getContext("2d");

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        if (ctx) {
          ctx.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
          video.pause();
          resolve(canvas.toDataURL("image/jpeg"));
          URL.revokeObjectURL(video.src);
        }
      };
    });
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setVideoUrl(url);

      try {
        const thumbnail = await generateVideoThumbnail(file);
        setPreviewVideo(thumbnail);
      }
      catch (err) {
        console.error("Error generating thumbnail", err);
      }
    }
  };

  const handleUpload = async () => {
    if (!videoUrl) return;
    setIsLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1500));

      setIsLoading(false);
      setActiveCard(2);
      setPreviewVideo(null);
    }
    catch (err: any) {
      setIsLoading(false);
      setError(err);
    }
  };

  const handleReset = () => {
    setActiveCard(1);
    setPreviewVideo(null);
    setVideoUrl(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <div
      ref={containerRef}
      onScroll={handleScroll}
      className={`h-dvh overflow-y-auto bg-linear-to-t no-scrollbar from-background from-0% to-[#242323] bg-local ${isSnapping ? 'snap-y snap-mandatory' : ''}`}
    >

      <Sidebar activeTab={activeTab} onNavigate={handleNavigate} />

      <div className="fixed h-full w-16 md:w-24 xl:w-32 flex items-center justify-center pointer-events-none z-10">
        <div className="rotate-180 [writing-mode:vertical-lr] flex items-center justify-center">
          <AnimatePresence mode='wait'>
            <motion.h2
              key={activeTab}
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -40 }}
              transition={{ duration: 0.4, ease: "easeInOut" }}
              className="font-heading font-black text-4xl text-highlight/80 tracking-tighter uppercase whitespace-nowrap md:text-5xl xl:text-6xl"
            >
              {activeTab === 'CHECK' ? 'Anomaly Check' : 'Anomaly History'}
            </motion.h2>
          </AnimatePresence>
        </div>
      </div>

      <section
        ref={checkRef}
        className="h-dvh w-full flex flex-col items-center justify-center pl-18 pr-18 md:pl-24 md:pr-24 xl:pl-32 xl:pr-32 snap-start overflow-hidden"
      >
        <AnimatePresence mode="wait">
          {activeCard === 1 ? (
            <motion.div
              key="card1"
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              transition={{ duration: 0.5, ease: "easeInOut" }}
              className="w-full flex flex-col md:max-w-lg max-w-sm"
            >
              <div className="bg-card aspect-square rounded-md border border-text/20 flex items-center justify-center group cursor-pointer p-4"
                onClick={() => fileInputRef.current?.click()}>
                <div className="w-full h-full border-dashed p-0.5 border sm:border-2 border-text/50 rounded-md group-hover:border-highlight/60 duration-300 transition-colors flex items-center justify-center relative overflow-hidden">
                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileChange}
                    accept=".mp4"
                    className="hidden"
                  />
                  {previewVideo ? (
                    <motion.img
                      key={previewVideo}
                      initial={{ opacity: 0, scale: 0 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{
                        duration: 0.3,
                        ease: "easeInOut"
                      }}
                      src={previewVideo}
                      className="absolute inset-0 w-full h-full object-cover rounded-sm"
                      alt="Preview"
                    />
                  ) : (
                    <div className="flex flex-col items-center gap-4">
                      <FaUpload className="text-text/50 text-xl sm:text-4xl group-hover:text-highlight/60 transition-colors duration-300" />
                      <span className="text-text/50 text-xs sm:text-sm md:text-xl uppercase tracking-widest font-sans group-hover:text-highlight/60 duration-300">
                        Upload Video
                      </span>
                    </div>
                  )}
                </div>
              </div>
              <SubmitButton onClick={handleUpload} disabled={isLoading} style={{ width: "50%", alignSelf: "center", marginTop: "2rem" }}>
                {isLoading ? (
                  <AiOutlineLoading3Quarters className="animate-spin text-2xl" />
                ) : (
                  'UPLOAD'
                )}
              </SubmitButton>
            </motion.div>
          ) : (
            <motion.div
              key="card2"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 50 }}
              transition={{ duration: 0.5, ease: "easeInOut" }}
              className="w-full flex flex-col md:max-w-lg max-w-sm"
            >
              <div className="bg-card aspect-3/4 md:aspect-square rounded-md border border-text/20 flex flex-col items-center p-4 gap-4">
                <div className="w-full flex items-center justify-between border-b border-text/20 pb-4">
                  <span className="text-text/60 text-xs uppercase tracking-widest">Status</span>
                  <div className="flex items-center gap-2 pointer-events-none">
                    <div className="w-2 h-2 rounded-full bg-success shadow-[0_0_8px] shadow-success"></div>
                    <span className="text-success font-heading font-bold tracking-wider text-sm">NORMAL</span>
                  </div>
                </div>

                <div className="w-full flex-1 bg-black/40 rounded-sm border border-text/30 relative overflow-hidden group min-h-0">
                  {videoUrl && (
                    <video
                      src={videoUrl}
                      controls
                      className="absolute inset-0 w-full h-full object-contain"
                      autoPlay
                    />
                  )}
                </div>

                <div className="w-full flex items-center justify-between">
                  <div className="flex flex-col">
                    <span className="text-text/60 text-[10px] uppercase tracking-wider">Accuracy</span>
                    <span className="text-text font-mono text-sm">98.4%</span>
                  </div>
                  {/* <div className="flex flex-col items-end">
                    <span className="text-text/40 text-[10px] uppercase tracking-wider">Duration</span>
                    <span className="text-text font-mono text-sm">00:12</span>
                  </div> */}
                </div>
              </div>

              <SubmitButton onClick={handleReset} style={{ width: "50%", alignSelf: "center", marginTop: "2rem" }}>
                BACK
              </SubmitButton>
            </motion.div>
          )}
        </AnimatePresence>
      </section>

      <section
        ref={historyRef}
        className="h-dvh w-full flex items-center justify-center pl-18 pr-18 md:pl-24 md:pr-24 xl:pl-32 xl:pr-32 snap-start"
      >
        <div className="w-full max-w-5xl">
          <div className="grid grid-cols-2 gap-8 w-full">
            <div className="h-48 bg-primary rounded-sm border border-zinc-800 flex items-center justify-center">
              <span className="text-zinc-700 font-mono text-xs italic">Record_001.data</span>
            </div>
            <div className="h-48 bg-primary rounded-sm border border-zinc-800 flex items-center justify-center">
              <span className="text-zinc-700 font-mono text-xs italic">Record_002.data</span>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
};

export default Home;