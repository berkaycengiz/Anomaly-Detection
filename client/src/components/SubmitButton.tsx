import React from "react";

interface SubmitButtonProps {
    onClick?: () => void;
    children: React.ReactNode;
    style?: React.CSSProperties;
    disabled?: boolean;
}

const SubmitButton: React.FC<SubmitButtonProps> = ({ children, onClick, style, disabled }) => {
  return (
    <button
    type="submit"
    onClick={onClick}
    style={style}
    disabled={disabled}
    className={`w-full flex flex-col items-center bg-highlight text-white text-md py-2 rounded-lg font-semibold transition duration-300 ${
      disabled
        ? 'opacity-50'
        : 'hover:bg-highlight/70 cursor-pointer'
    }`}>
        {children}
    </button>
  );
};

export default SubmitButton;
