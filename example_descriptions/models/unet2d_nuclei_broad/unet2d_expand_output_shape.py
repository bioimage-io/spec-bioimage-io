# type: ignore
import torch
import torch.nn as nn


class Upsample(nn.Module):
    def __init__(self, scale_factor, mode="bilinear"):
        super().__init__()
        self.scale_factor = scale_factor
        self.mode = mode

    def forward(self, input):
        return nn.functional.interpolate(
            input, scale_factor=self.scale_factor, mode=self.mode, align_corners=False
        )


class UNet2d(nn.Module):
    def __init__(self, input_channels, output_channels, training=False):
        super().__init__()
        self.input_channels = input_channels
        self.output_channels = output_channels
        self.n_levels = 3

        self.encoders = nn.ModuleList(
            [
                self.conv_layer(self.input_channels, 16),
                self.conv_layer(16, 32),
                self.conv_layer(32, 64),
            ]
        )
        self.downsamplers = nn.ModuleList([self.downsampler()] * self.n_levels)

        self.base = self.conv_layer(64, 128)

        self.decoders = nn.ModuleList(
            [self.conv_layer(128, 64), self.conv_layer(64, 32), self.conv_layer(32, 16)]
        )
        self.upsamplers = nn.ModuleList(
            [self.upsampler(128, 64), self.upsampler(64, 32), self.upsampler(32, 16)]
        )

        self.output = nn.Conv2d(16, self.output_channels, 1)
        self.training = training

    def conv_layer(self, in_channels, out_channels):
        kernel_size = 3
        padding = 1
        return nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size, padding=padding),
            nn.Conv2d(out_channels, out_channels, kernel_size, padding=padding),
            nn.ReLU(inplace=True),
        )

    def downsampler(self):
        return nn.MaxPool2d(2)

    def upsampler(self, in_channels, out_channels):
        return nn.Sequential(Upsample(2), nn.Conv2d(in_channels, out_channels, 1))

    def forward(self, input):
        x = input

        from_encoder = []
        for encoder, sampler in zip(self.encoders, self.downsamplers):
            x = encoder(x)
            from_encoder.append(x)
            x = sampler(x)

        x = self.base(x)

        for decoder, sampler, enc in zip(
            self.decoders, self.upsamplers, from_encoder[::-1]
        ):
            x = sampler(x)
            x = torch.cat([enc, x], dim=1)
            x = decoder(x)

        x = self.output(x)

        # apply a sigmoid directly if we are in inference mode
        if not self.training:
            # postprocessing
            x = torch.sigmoid(x)

        # expand the shape across z
        out_shape = tuple(x.shape)
        expanded_shape = out_shape[:2] + (1,) + out_shape[2:]
        return x.expand(expanded_shape)
