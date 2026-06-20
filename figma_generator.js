// Figma Plugin Console Script
// To run this, open Figma, open the Developer Console (Figma > Plugins > Development > Open Console),
// and paste this code. Press Enter to execute.

async function generateCarousel() {
  console.log("Starting Figma Carousel Generator...");
  
  // 1. Define Design System Colors
  const black = { r: 10/255, g: 10/255, b: 10/255 };
  const charcoal = { r: 28/255, g: 28/255, b: 28/255 };
  const offWhite = { r: 245/255, g: 244/255, b: 240/255 };
  const spiritBlue = { r: 46/255, g: 91/255, b: 255/255 };
  const burntGold = { r: 201/255, g: 149/255, b: 44/255 };
  const darkGray = { r: 180/255, g: 180/255, b: 180/255 };

  // 2. Load Required Fonts
  console.log("Loading fonts...");
  try {
    await Promise.all([
      figma.loadFontAsync({ family: "Inter", style: "Bold" }),
      figma.loadFontAsync({ family: "Inter", style: "Regular" }),
      figma.loadFontAsync({ family: "Playfair Display", style: "Italic" }),
      figma.loadFontAsync({ family: "Playfair Display", style: "Regular" }),
      figma.loadFontAsync({ family: "Poppins", style: "Bold" }),
      figma.loadFontAsync({ family: "Poppins", style: "Regular" })
    ]);
  } catch (err) {
    console.error("Font load failed. Trying system fallbacks...", err);
    // Fallback loading standard Inter/Helvetica if Playfair or Poppins fail
    await Promise.all([
      figma.loadFontAsync({ family: "Inter", style: "Bold" }),
      figma.loadFontAsync({ family: "Inter", style: "Regular" })
    ]);
  }

  // Helper: Setup Frame
  function createSlideFrame(name, x) {
    const frame = figma.createFrame();
    frame.name = name;
    frame.resize(1080, 1350);
    frame.x = x;
    frame.y = 0;
    frame.backgrounds = [{ type: 'SOLID', color: black }];
    figma.currentPage.appendChild(frame);
    return frame;
  }

  // Helper: Create Text Node
  function drawText(parent, characters, x, y, size, fontName, color, options = {}) {
    const text = figma.createText();
    parent.appendChild(text);
    text.fontName = fontName;
    text.characters = characters;
    text.fontSize = size;
    text.fills = [{ type: 'SOLID', color: color }];
    
    if (options.width) {
      text.resize(options.width, text.height);
      text.textAutoResize = "HEIGHT";
    }
    
    text.x = x;
    text.y = y;

    if (options.align) {
      text.textAlignHorizontal = options.align;
    }
    if (options.letterSpacing) {
      text.letterSpacing = { value: options.letterSpacing, unit: "PERCENT" };
    }
    if (options.lineHeight) {
      text.lineHeight = { value: options.lineHeight, unit: "PIXELS" };
    }
    return text;
  }

  // Helper: Drawing a line-art silhouette pose (Vrksasana / Tree Pose)
  function drawTreePose(parent, cx, cy) {
    const nodes = [];

    // Head
    const head = figma.createEllipse();
    head.resize(32, 32);
    head.x = cx - 16;
    head.y = cy - 140;
    head.fills = [{ type: 'SOLID', color: offWhite }];
    parent.appendChild(head);
    nodes.push(head);

    // Spine
    const spine = figma.createVector();
    spine.vectorPaths = [{
      windingRule: "NONZERO",
      data: `M ${cx} ${cy - 100} L ${cx} ${cy + 20}`
    }];
    spine.strokes = [{ type: 'SOLID', color: offWhite }];
    spine.strokeWeight = 3;
    parent.appendChild(spine);
    nodes.push(spine);

    // Arms in Anjali Mudra (Prayer over head)
    const arms = figma.createVector();
    arms.vectorPaths = [{
      windingRule: "NONZERO",
      data: `M ${cx - 20} ${cy - 70} Q ${cx - 50} ${cy - 120} ${cx} ${cy - 160} Q ${cx + 50} ${cy - 120} ${cx + 20} ${cy - 70}`
    }];
    arms.strokes = [{ type: 'SOLID', color: offWhite }];
    arms.strokeWeight = 2;
    parent.appendChild(arms);
    nodes.push(arms);

    // Support Leg (Standing straight)
    const leg1 = figma.createVector();
    leg1.vectorPaths = [{
      windingRule: "NONZERO",
      data: `M ${cx} ${cy + 20} L ${cx} ${cy + 140}`
    }];
    leg1.strokes = [{ type: 'SOLID', color: offWhite }];
    leg1.strokeWeight = 3;
    parent.appendChild(leg1);
    nodes.push(leg1);

    // Bent Leg (Foot touching knee)
    const leg2 = figma.createVector();
    leg2.vectorPaths = [{
      windingRule: "NONZERO",
      data: `M ${cx} ${cy + 20} Q ${cx - 50} ${cy + 60} ${cx} ${cy + 80}`
    }];
    leg2.strokes = [{ type: 'SOLID', color: offWhite }];
    leg2.strokeWeight = 3;
    parent.appendChild(leg2);
    nodes.push(leg2);

    // Heart chakra glowing dot
    const heart = figma.createEllipse();
    heart.resize(8, 8);
    heart.x = cx - 4;
    heart.y = cy - 60;
    heart.fills = [{ type: 'SOLID', color: spiritBlue }];
    parent.appendChild(heart);
    nodes.push(heart);

    const group = figma.group(nodes, parent);
    group.name = "TreePose_Silhouette";
    return group;
  }

  // Helper: Draw Footers (Consistent layout)
  function drawFooter(frame, textStr) {
    // 80px safe area bottom limit
    const footerY = 1350 - 80 - 24;
    drawText(frame, textStr, 80, footerY, 13, { family: "Inter", style: "Regular" }, darkGray, {
      letterSpacing: 10,
      width: 1080 - 160,
      align: "CENTER"
    });
  }

  // ==========================================
  // SLIDE 1 — COVER
  // ==========================================
  console.log("Generating Slide 1...");
  const s1 = createSlideFrame("Slide_1_Cover", 0);

  // Background circle in Spirit blue (15% opacity)
  const bgCircle = figma.createEllipse();
  bgCircle.resize(480, 480);
  bgCircle.x = 540 - 240;
  bgCircle.y = 750 - 240;
  bgCircle.fills = [{ type: 'SOLID', color: spiritBlue }];
  bgCircle.opacity = 0.15;
  s1.appendChild(bgCircle);

  // Concentric breath-wave rings radiating outward
  const rings = [];
  for (let i = 1; i <= 6; i++) {
    const r = 160 + i * 45;
    const ring = figma.createEllipse();
    ring.resize(r * 2, r * 2);
    ring.x = 540 - r;
    ring.y = 750 - r;
    ring.strokes = [{ type: 'SOLID', color: offWhite }];
    ring.strokeWeight = 1;
    ring.opacity = 0.25 - (i * 0.03);
    s1.appendChild(ring);
    rings.push(ring);
  }
  const waveGroup = figma.group(rings, s1);
  waveGroup.name = "BreathWaves";

  // Neural pathways (circuit-like lines radiating from chest)
  const pathways = figma.createVector();
  pathways.name = "NeuralPathways";
  pathways.vectorPaths = [
    { windingRule: "NONZERO", data: "M 540 690 Q 480 680 430 730 L 400 730" },
    { windingRule: "NONZERO", data: "M 540 690 Q 600 680 650 730 L 680 730" },
    { windingRule: "NONZERO", data: "M 540 690 Q 510 630 460 610 L 430 610" },
    { windingRule: "NONZERO", data: "M 540 690 Q 570 630 620 610 L 650 610" }
  ];
  pathways.strokes = [{ type: 'SOLID', color: spiritBlue }];
  pathways.strokeWeight = 1.5;
  pathways.opacity = 0.6;
  s1.appendChild(pathways);

  // Draw Figure
  drawTreePose(s1, 540, 750);

  // Typography
  drawText(s1, "YOGA: THE ORIGINAL HUMAN TECHNOLOGY", 80, 160, 48, { family: "Inter", style: "Bold" }, offWhite, {
    width: 1080 - 160,
    lineHeight: 56,
    letterSpacing: 2
  });

  drawText(s1, "Refining awareness for over five millennia.", 80, 290, 22, { family: "Playfair Display", style: "Italic" }, offWhite, {
    width: 1080 - 160
  });

  drawText(s1, "Long before algorithms measured performance, yoga explored the most sophisticated system ever created: the human body and mind.", 80, 360, 16, { family: "Inter", style: "Regular" }, darkGray, {
    width: 680,
    lineHeight: 26
  });

  drawFooter(s1, "INTERNATIONAL YOGA DAY 2026 • SPIRIT, IIT GUWAHATI");


  // ==========================================
  // SLIDE 2 — ATHLETE'S INVISIBLE TRAINING
  // ==========================================
  console.log("Generating Slide 2...");
  const s2 = createSlideFrame("Slide_2_Training", 1200);

  // Vertical divide line
  const divider = figma.createLine();
  divider.x = 540;
  divider.y = 80;
  divider.resize(1190, 0); // length is height
  divider.rotation = 90;
  divider.strokes = [{ type: 'SOLID', color: charcoal }];
  divider.strokeWeight = 1.5;
  s2.appendChild(divider);

  // Left Content
  drawText(s2, "THE ATHLETE'S INVISIBLE TRAINING", 80, 160, 32, { family: "Inter", style: "Bold" }, offWhite, {
    width: 380,
    lineHeight: 40
  });

  const listItems = [
    { main: "Strength trains muscles.", sub: "Yoga trains:" },
    { main: "Breath under pressure", sub: "" },
    { main: "Focus amidst distraction", sub: "" },
    { main: "Recovery beyond fatigue", sub: "" },
    { main: "Balance through uncertainty", sub: "" },
    { main: "Awareness within movement", sub: "" }
  ];

  let currentY = 270;
  listItems.forEach((item, idx) => {
    // Write text
    if (idx === 0) {
      drawText(s2, item.main, 80, currentY, 18, { family: "Inter", style: "Bold" }, offWhite);
      currentY += 28;
      drawText(s2, item.sub, 80, currentY, 18, { family: "Playfair Display", style: "Italic" }, spiritBlue);
      currentY += 40;
    } else {
      drawText(s2, item.main, 80, currentY, 16, { family: "Inter", style: "Regular" }, offWhite);
      currentY += 36;
    }

    // Horizontal separator
    if (idx < listItems.length - 1) {
      const line = figma.createLine();
      line.x = 80;
      line.y = currentY;
      line.resize(380, 0);
      line.strokes = [{ type: 'SOLID', color: charcoal }];
      line.strokeWeight = 1;
      s2.appendChild(line);
      currentY += 20;
    }
  });

  drawText(s2, "Peak performance begins long before the first move.", 80, 1060, 18, { family: "Playfair Display", style: "Italic" }, offWhite, {
    width: 380,
    lineHeight: 26
  });

  // Right Content (Athlete Morphing Posture)
  // Dynamic runner (dotted outline) morphing into stable yoga pose
  const morphNodes = [];

  // 1. Deep background blur aura
  const rightAura = figma.createEllipse();
  rightAura.resize(300, 300);
  rightAura.x = 810 - 150;
  rightAura.y = 675 - 150;
  rightAura.fills = [{ type: 'SOLID', color: spiritBlue }];
  rightAura.opacity = 0.08;
  rightAura.effects = [{ type: 'LAYER_BLUR', radius: 80, visible: true }];
  s2.appendChild(rightAura);
  morphNodes.push(rightAura);

  // 2. Runner phase (faded, dynamic movement silhouette)
  const runner = figma.createVector();
  runner.vectorPaths = [{
    windingRule: "NONZERO",
    data: "M 740 760 L 760 700 L 800 660 L 790 620 M 800 660 L 840 680 L 870 650 M 760 700 L 720 720 L 690 760"
  }];
  runner.strokes = [{ type: 'SOLID', color: offWhite }];
  runner.strokeWeight = 1.5;
  runner.opacity = 0.25;
  s2.appendChild(runner);
  morphNodes.push(runner);

  // 3. Warrior pose phase (strong outline posture)
  const warrior = figma.createVector();
  warrior.vectorPaths = [{
    windingRule: "NONZERO",
    // Beautiful geometric lines for Warrior II Pose (Virabhadrasana II)
    data: `
      M 810 590 L 810 560 
      M 810 590 L 810 680 
      M 810 610 L 730 610 
      M 810 610 L 890 610 
      M 810 680 L 730 730 L 730 790 
      M 810 680 L 880 720 L 920 790
    `
  }];
  warrior.strokes = [{ type: 'SOLID', color: offWhite }];
  warrior.strokeWeight = 3;
  warrior.opacity = 0.9;
  s2.appendChild(warrior);
  morphNodes.push(warrior);

  // Glow point at head of warrior
  const headGlow = figma.createEllipse();
  headGlow.resize(10, 10);
  headGlow.x = 810 - 5;
  headGlow.y = 560 - 5;
  headGlow.fills = [{ type: 'SOLID', color: spiritBlue }];
  s2.appendChild(headGlow);
  morphNodes.push(headGlow);

  const morphGroup = figma.group(morphNodes, s2);
  morphGroup.name = "Athlete_Morphing_Posture";

  drawFooter(s2, "INTERNATIONAL YOGA DAY 2026 • SPIRIT, IIT GUWAHATI");


  // ==========================================
  // SLIDE 3 — SANSKRIT CLOSER
  // ==========================================
  console.log("Generating Slide 3...");
  const s3 = createSlideFrame("Slide_3_Sanskrit", 2400);

  // Premium background radial aura (Burnt Gold)
  const goldAura = figma.createEllipse();
  goldAura.resize(500, 500);
  goldAura.x = 540 - 250;
  goldAura.y = 675 - 250;
  goldAura.fills = [{ type: 'SOLID', color: burntGold }];
  goldAura.opacity = 0.07;
  goldAura.effects = [{ type: 'LAYER_BLUR', radius: 120, visible: true }];
  s3.appendChild(goldAura);

  // Meditation pose vector paths in background (subtle outline overlay)
  const backgroundFigure = figma.createVector();
  backgroundFigure.vectorPaths = [{
    windingRule: "NONZERO",
    data: "M 540 550 L 540 680 M 540 580 L 480 610 L 500 660 M 540 580 L 600 610 L 580 660 M 540 680 L 460 740 L 540 760 M 540 680 L 620 740 L 540 760"
  }];
  backgroundFigure.strokes = [{ type: 'SOLID', color: offWhite }];
  backgroundFigure.strokeWeight = 2;
  backgroundFigure.opacity = 0.15;
  s3.appendChild(backgroundFigure);

  // Center Content
  // Sanskrit Verse (Sanskrit font used: Poppins or standard fallback)
  drawText(s3, "योगः कर्मसु कौशलम्", 80, 420, 64, { family: "Poppins", style: "Bold" }, burntGold, {
    width: 1080 - 160,
    align: "CENTER"
  });

  drawText(s3, "Yoga is excellence in action. — Bhagavad Gita 2.50", 80, 530, 20, { family: "Playfair Display", style: "Italic" }, offWhite, {
    width: 1080 - 160,
    align: "CENTER"
  });

  drawText(s3, "Yoga is not an escape from action. It is the discipline that brings clarity to action, presence to movement, and purpose to performance. In stillness, we discover the strength that sustains every pursuit.", 190, 640, 20, { family: "Inter", style: "Regular" }, offWhite, {
    width: 700,
    lineHeight: 34,
    align: "CENTER"
  });

  drawFooter(s3, "Breathe with intention. Move with awareness. Happy International Yoga Day. — Spirit, IIT Guwahati");

  // Select all 3 frames in user's viewport
  figma.viewport.scrollAndZoomIntoView([s1, s2, s3]);
  console.log("Carousel Generated Successfully!");
  figma.notify("Spirit Yoga Carousel Generated Natively!");
}

// Execute generator
generateCarousel();
