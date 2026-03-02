export default class Bullet {
  constructor(scene, x, y, speed) {
    this.scene = scene;
    this.speed = speed;
    this.sprite = scene.add.rectangle(x, y, 4, 12, 0xffffff);
    scene.physics.add.existing(this.sprite);

    this.sprite.body.setAllowGravity(false);
  }

  update() {
    this.sprite.y -= this.speed * 0.016;
  }

  isOffScreen() {
    return this.sprite.y < 0;
  }

  destroy() {
    this.sprite.destroy();
  }
}
