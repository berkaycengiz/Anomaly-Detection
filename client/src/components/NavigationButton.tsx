import React from "react";

interface NavigationButtonProps {
    onClick?: () => void;
    children: React.ReactNode;
    style?: React.CSSProperties;
    disabled?: boolean;
}

const NavigationButton: React.FC<NavigationButtonProps> = ({ onClick, children, style, disabled }) => {
  return (
    <button
    type="button"
    onClick={onClick}
    style={style}
    disabled={disabled}
    className={`w-10 h-10 flex flex-col items-center self-center rounded-full bg-highlight text-white justify-center transition duration-300 ${
      disabled
        ? 'opacity-50'
        : 'hover:bg-highlight/60 hover:text-white/80 hover:cursor-pointer'
    }`}>
        {children}
    </button>
  );
};

export default NavigationButton;