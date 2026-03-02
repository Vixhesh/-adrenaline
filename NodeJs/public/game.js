import Ship from "./js/Ship.js";
import Bullet from "./js/Bullet.js";
import Alien from "./js/Alien.js";
import Settings from "./js/Settings.js";

const config = {
  type: Phaser.AUTO,
  width: 1080,
  height: 600,
  physics: { default: "arcade" },
  scene: { preload, create, update }
};

let ship, cursors, fireKey;
let lastSpawnY = 0;
let bullets = [];
// let aliens = [];
let settings;
let isPaused=true;
let playButton;
let uiClicked=false;

let fleetDirection = 1;  

function preload() {
  this.load.image("ship", "assets/ship.bmp");
  this.load.image("alien", "assets/alien.bmp");
}

function create() {
  settings = new Settings();
  this.aliens = aliens;
  ship = new Ship(this);
  this.cameras.main.setBackgroundColor("#ffffff");

  cursors = this.input.keyboard.createCursorKeys();
  fireKey = this.input.keyboard.addKey(
    Phaser.Input.Keyboard.KeyCodes.SPACE
  );

  this.input.on("pointerdown", fireBullet, this);

  // createFleet.call(this);
  // 🔴 Fleet will be created after Play is pressed
  this.physics.pause();
    playButton = this.add.circle(
    this.scale.width / 2,
    this.scale.height / 2,
    40,
    0x00ff00
  ).setInteractive();

  playButton.text = this.add.text(
    playButton.x - 10,
    playButton.y - 14,
    "▶",
    { fontSize: "30px", color: "#000" }
  ); 

  playButton.on("pointerdown", toggleGameState, this);
}

function createFleet() {
  aliens = [];                     

  const startX = 80;
  const startY = 80;
  const gapX = 70;
  const gapY = 60;

  const rows = 1;                 

  for (let row = 0; row < rows; row++) {           
    for (let x = startX; x <= 1000; x += gapX) {
      const alien = new Alien(
        this,
        x,
        startY + row * gapY         
      );
      aliens.push(alien);
    }
  }

  fleetDirection = 1;             
}



function fireBullet() {
  if (uiClicked || isPaused) return;
  if (bullets.length >= settings.bulletsAllowed) return;

  const bullet = new Bullet(
    this,
    ship.sprite.x,
    ship.sprite.y - 20,
    settings.bulletSpeed
  );

  bullets.push(bullet);
}

function update() {
  if (isPaused){
    ship.sprite.setVelocity(0);
    return;
  }  
  ship.update(cursors, settings.shipSpeed);
  bullets.forEach((bullet, i) => {
    bullet.update();
    if (bullet.isOffScreen()) {
      bullet.destroy();
      bullets.splice(i, 1);
    }
  });

    
  bullets.forEach((bullet, bIndex) => {
    aliens.forEach((alien, aIndex) => {
      if (isColliding(bullet, alien)) {
        bullet.destroy();               
        alien.destroy();                

        bullets.splice(bIndex, 1);      
        aliens.splice(aIndex, 1);       
      }
    });
  });
  aliens.forEach(alien => {
  if (isColliding({ sprite: ship.sprite }, alien)) {
    console.log("Ship Hit!");      // 🔴 NEW
    this.physics.pause();          
    isPaused = true;      
    console.log("Collision detected");          
  }
});
   

  let edgeHit = false;

  aliens.forEach((alien) => {
     
    alien.update(settings.alienSpeed, fleetDirection);
    if (alien.checkEdges()) edgeHit = true;
  });

  if (edgeHit) {
    fleetDirection *= -1;
    aliens.forEach((alien) => {
      alien.dropDown(20);
    });
  }

  if (Phaser.Input.Keyboard.JustDown(fireKey)) {
    fireBullet.call(this);
  }
  let lowestAlienY = 0;
aliens.forEach(alien => {
  if (alien.sprite.y > lowestAlienY) {
    lowestAlienY = alien.sprite.y;
  }
});

if (lowestAlienY - lastSpawnY > 60) {                 // 🔴 MODIFIED
  settings.increaseSpeed();               // 🔴 NEW
  createFleet.call(this);                 // 🔴 spawn new row
lastSpawnY = lowestAlienY; 
}

}
function isColliding(obj1,obj2){
   return Phaser.Geom.Intersects.RectangleToRectangle(
    obj1.sprite.getBounds(),
    obj2.sprite.getBounds()
  );
}
function toggleGameState() {
  uiClicked = true;                

if (isPaused) {
    if (!aliens || aliens.length === 0) {     // 🔴 NEW
    createFleet.call(this);      // 🔴 NEW
    }  
    this.physics.resume();           
    isPaused = false;                
    playButton.setPosition(
      this.scale.width - 50,
      50
    );    
                            
    playButton.text.setPosition(
      playButton.x - 12,
      playButton.y - 14
    );                              
    playButton.text.setText("⏸");    
  } else {
    this.physics.pause();           
    isPaused = true;                
    playButton.text.setText("▶");    
  }
  setTimeout(() => {
    uiClicked = false;               
  }, 50);
}

new Phaser.Game(config);
