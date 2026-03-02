export default class Ship {
  constructor(scene) {
    this.scene = scene;
    this.sprite = scene.physics.add.sprite(540, 550, "ship");
    this.sprite.setCollideWorldBounds(true);
  }

  update(cursors, speed) {
    this.sprite.setVelocityX(0);
    if (cursors.left.isDown) this.sprite.setVelocityX(-speed);
    if (cursors.right.isDown) this.sprite.setVelocityX(speed);
  }
}
