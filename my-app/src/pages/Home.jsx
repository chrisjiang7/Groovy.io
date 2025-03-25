import { useState, useEffect } from 'react';
import logo from '../assets/logo.png';

const Home = () => {
  const [displayDescription, setDisplayDescription] = useState('');
  const [displayInstruction, setDisplayInstruction] = useState('');
  const descriptionText = "Your personal AI powered DJ ready to remix your favorite songs with the click of a button!";
  const instructionText = "To get started, press one of the buttons below ⬇️";
  const [descIndex, setDescIndex] = useState(0);
  const [instrIndex, setInstrIndex] = useState(0);

  // Animates the description text
  useEffect(() => {
    if (descIndex < descriptionText.length) {
      const timeout = setTimeout(() => {
        setDisplayDescription(prev => prev + descriptionText[descIndex]);
        setDescIndex(prev => prev + 1);
      }, 30); // Faster typing speed

      return () => clearTimeout(timeout);

    } else if (descIndex === descriptionText.length && instrIndex === 0) {
      // start instructions animation after description finishes
      const delay = setTimeout(() => {
        setInstrIndex(1); // start the second animation
      }, 500); // pause between animations
      return () => clearTimeout(delay);
    }
  }, [descIndex, descriptionText]);

  // animate instruction text
  useEffect(() => {
    if (instrIndex > 0 && instrIndex <= instructionText.length) {
      const timeout = setTimeout(() => {
        setDisplayInstruction(prev => prev + instructionText[instrIndex - 1]);
        setInstrIndex(prev => prev + 1);
      }, 50); // lower typing speed for instructions

      return () => clearTimeout(timeout);
    }
  }, [instrIndex, instructionText]);

  return (
    <div className="flex flex-col items-center justify-center text-center p-8 pb-24">
      <h1 className="text-5xl font-bold text-purple-400 mb-8">Welcome to Groovy!</h1>
      
      <img
        src={logo}
        alt="Groovy Logo"
        className="w-80 h-70 mb-6 rounded-full transition duration-300 hover:shadow-[0_0_25px_5px_rgba(255,255,255,0.7)] object-contain"
      />

      <p className="max-w-xl font-bold mb-15 text-lg text-purple-400 min-h-[120px]">
        {displayDescription}
        {descIndex < descriptionText.length && (
          <span className="animate-pulse">|</span>
        )}
      </p>

      <p className="text-lg font-bold text-cyan-300 mb-2 min-h-[28px]">
        {displayInstruction}
        {instrIndex > 0 && instrIndex <= instructionText.length && (
          <span className="animate-pulse">|</span>
        )}
      </p>
    </div>
  );
};

export default Home;