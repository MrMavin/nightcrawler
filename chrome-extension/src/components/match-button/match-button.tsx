import React, { useState, useEffect } from 'react';

interface MatchButtonProps {
  isJobPage: boolean;
  saveButton: HTMLElement | null;
  onAnalyzeMatch: () => void;
}

const MatchButton: React.FC<MatchButtonProps> = ({ isJobPage, saveButton, onAnalyzeMatch }) => {
  const [showMatchButton, setShowMatchButton] = useState(false);

  useEffect(() => {
    if (isJobPage && saveButton) {
      setShowMatchButton(true);
    } else {
      setShowMatchButton(false);
    }
  }, [isJobPage, saveButton]);

  const handleSeeMatch = () => {
    console.log('🎯 See Match button clicked!');
    onAnalyzeMatch();
  };

  if (!showMatchButton) return null;

  const buttonStyle: React.CSSProperties = {
    display: 'inline-flex',
    alignItems: 'center',
    padding: '8px 16px',
    marginLeft: '8px',
    fontSize: '14px',
    fontWeight: '500',
    color: 'white',
    backgroundColor: '#16a34a',
    border: 'none',
    borderRadius: '6px',
    boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    cursor: 'pointer',
    transition: 'background-color 0.2s ease-in-out',
    zIndex: 9999,
    position: 'relative',
    fontFamily: 'system-ui, -apple-system, sans-serif'
  };

  const spanStyle: React.CSSProperties = {
    marginRight: '4px'
  };

  return (
    <button
      onClick={handleSeeMatch}
      style={buttonStyle}
      onMouseEnter={(e) => {
        e.currentTarget.style.backgroundColor = '#15803d';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.backgroundColor = '#16a34a';
      }}
    >
      <span style={spanStyle}>🎯</span>
      See Match
    </button>
  );
};

export default MatchButton;