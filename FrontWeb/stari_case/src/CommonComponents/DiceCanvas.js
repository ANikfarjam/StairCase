// src/components/DiceCanvas.js
import React from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Box } from "@react-three/drei";

const Dice = () => {
  return (
    <Box args={[1, 1, 1]} rotation={[Math.PI / 4, Math.PI / 4, 0]}>
      <meshStandardMaterial attach="material" color="#fff" />
    </Box>
  );
};

const DiceCanvas = () => {
  return (
    <div style={{ position: "absolute", top: 20, right: 20, width: 150, height: 150 }}>
      <Canvas>
        <ambientLight intensity={0.5} />
        <directionalLight position={[2, 2, 2]} />
        <Dice />
        <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={2} />
      </Canvas>
    </div>
  );
};

export default DiceCanvas;
